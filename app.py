
import os

import mysql.connector
from dotenv import load_dotenv

load_dotenv()


def connect_to_database():
    """Connect to the election database."""
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
    )


def get_polling_unit_results(polling_unit_id):
    """Display recorded election results for one polling unit."""
    connection = connect_to_database()
    cursor = connection.cursor(dictionary=True)

    
    query = """
        SELECT
            pu.uniqueid,
            pu.polling_unit_name,
            lga.lga_name,
            results.party_abbreviation,
            SUM(results.party_score) AS total_votes
        FROM polling_unit AS pu
        INNER JOIN lga
            ON pu.lga_id = lga.uniqueid
        INNER JOIN announced_pu_results AS results
            ON pu.uniqueid = results.polling_unit_uniqueid
        WHERE pu.uniqueid = %s
        GROUP BY
            pu.uniqueid,
            pu.polling_unit_name,
            lga.lga_name,
            results.party_abbreviation
        ORDER BY results.party_abbreviation
    """


    cursor.execute(query, (polling_unit_id,))
    results = cursor.fetchall()

    cursor.close()
    connection.close()

    if not results:
        print("No recorded results found for this polling unit.")
        return

    unit = results[0]

    print(f"\nPolling Unit: {unit['polling_unit_name']}")
    print(f"Polling Unit ID: {unit['uniqueid']}")
    print(f"LGA: {unit['lga_name']}")
    print("\nElection Results:")

    for result in results:
        print(
            f"{result['party_abbreviation']}: "
            f"{result['total_votes']} votes"
        )


def get_lga_results(lga_id):
    """Calculate party totals from polling-unit results."""
    connection = connect_to_database()
    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT
            lga.lga_name,
            results.party_abbreviation,
            SUM(results.party_score) AS total_votes
        FROM lga
        INNER JOIN polling_unit AS pu
            ON lga.uniqueid = pu.lga_id
        INNER JOIN announced_pu_results AS results
            ON pu.uniqueid = results.polling_unit_uniqueid
        WHERE lga.uniqueid = %s
        GROUP BY
            lga.lga_name,
            results.party_abbreviation
        ORDER BY results.party_abbreviation
    """

    cursor.execute(query, (lga_id,))
    results = cursor.fetchall()

    cursor.close()
    connection.close()

    if not results:
        print("No recorded polling-unit results found for this LGA.")
        return

    print(f"\nLGA: {results[0]['lga_name']}")
    print("\nSummed Polling-Unit Results:")

    for result in results:
        print(
            f"{result['party_abbreviation']}: "
            f"{result['total_votes']} votes"
        )



def add_polling_unit():
    """Create a polling unit and save its election results."""
    connection = connect_to_database()
    cursor = connection.cursor(dictionary=True)

    try:
        # Show available LGAs in Delta State.
        cursor.execute("""
            SELECT uniqueid, lga_name
            FROM lga
            WHERE state_id = 25
            ORDER BY lga_name
        """)
        lgas = cursor.fetchall()

        print("\nAvailable LGAs:")
        for lga in lgas:
            print(f"{lga['uniqueid']}. {lga['lga_name']}")

        lga_input = input("\nEnter the LGA database ID: ").strip()

        if not lga_input.isdigit():
            print("LGA ID must be a number.")
            return

        lga_id = int(lga_input)

        # Check that the selected LGA exists.
        cursor.execute(
            "SELECT uniqueid, lga_name FROM lga "
            "WHERE uniqueid = %s AND state_id = 25",
            (lga_id,),
        )
        selected_lga = cursor.fetchone()

        if not selected_lga:
            print("Invalid LGA ID.")
            return

        # Show wards belonging to that LGA.
        cursor.execute("""
            SELECT uniqueid, ward_name
            FROM ward
            WHERE lga_id = %s
            ORDER BY ward_name
        """, (lga_id,))
        wards = cursor.fetchall()

        if not wards:
            print("No wards found for this LGA.")
            return

        print(f"\nWards in {selected_lga['lga_name']}:")
        for ward in wards:
            print(f"{ward['uniqueid']}. {ward['ward_name']}")

        ward_input = input("\nEnter the ward database ID: ").strip()

        if not ward_input.isdigit():
            print("Ward ID must be a number.")
            return

        ward_id = int(ward_input)

        # Confirm that the ward belongs to the selected LGA.
        cursor.execute("""
            SELECT uniqueid, ward_id, ward_name
            FROM ward
            WHERE uniqueid = %s AND lga_id = %s
        """, (ward_id, lga_id))
        selected_ward = cursor.fetchone()

        if not selected_ward:
            print("Invalid ward for the selected LGA.")
            return

        unit_name = input("Enter polling unit name: ").strip()
        unit_number = input("Enter polling unit number: ").strip()

        if not unit_name or not unit_number:
            print("Polling unit name and number are required.")
            return

        # Read the party list from the database.
        cursor.execute(
            "SELECT partyid, partyname FROM party ORDER BY partyid"
        )
        parties = cursor.fetchall()

        party_scores = []

        
        for party in parties:
            abbreviation = party["partyid"]

            if abbreviation == "LABOUR":
                abbreviation = "LABO"

            while True:
                score_input = input(
                    f"Enter votes for {party['partyname']}: "
                ).strip()

                if score_input.isdigit():
                    party_scores.append((abbreviation, int(score_input)))
                    break

                print("Please enter a whole number of zero or more.")



        cursor.execute("""
            INSERT INTO polling_unit (
                polling_unit_id,
                ward_id,
                lga_id,
                uniquewardid,
                polling_unit_number,
                polling_unit_name,
                entered_by_user,
                date_entered,
                user_ip_address
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), %s)
        """, (
            0,
            selected_ward["ward_id"],
            lga_id,
            selected_ward["uniqueid"],
            unit_number,
            unit_name,
            "bincom_app",
            "127.0.0.1",
        ))


        new_unit_id = cursor.lastrowid

        for party_id, score in party_scores:
            cursor.execute("""
                INSERT INTO announced_pu_results (
                    polling_unit_uniqueid,
                    party_abbreviation,
                    party_score,
                    entered_by_user,
                    date_entered,
                    user_ip_address
                )
                VALUES (%s, %s, %s, %s, NOW(), %s)
            """, (
                str(new_unit_id),
                party_id,
                score,
                "bincom_app",
                "127.0.0.1",
            ))

        connection.commit()

        print("\nPolling unit and party results saved successfully!")
        print(f"New polling unit database ID: {new_unit_id}")
        print(f"LGA: {selected_lga['lga_name']}")
        print(f"Ward: {selected_ward['ward_name']}")
        print(f"Party result records saved: {len(party_scores)}")

    except mysql.connector.Error as error:
        connection.rollback()
        print(f"Database error. Changes rolled back: {error}")

    finally:
        cursor.close()
        connection.close()




print("\nDELTA STATE ELECTION RESULTS")
print("1. View results for a polling unit")
print("2. View summed results for an LGA")
print("3. Add a new polling unit and its results")

choice = input("Choose an option (1, 2 or 3): ").strip()

if choice == "1":
    polling_unit_id = input("Enter polling unit ID: ").strip()

    if polling_unit_id.isdigit():
        get_polling_unit_results(int(polling_unit_id))
    else:
        print("Please enter a valid numeric polling unit ID.")

elif choice == "2":
    lga_id = input("Enter LGA database ID: ").strip()

    if lga_id.isdigit():
        get_lga_results(int(lga_id))
    else:
        print("Please enter a valid numeric LGA ID.")

elif choice == "3":
    add_polling_unit()

else:
    print("Invalid choice. Please select 1, 2 or 3.")
