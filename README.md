# Bincom Election Results

A Python command-line application for viewing Delta State election results, calculating party vote totals by Local Government Area (LGA), and adding polling units with their party results.

## Features

1. View election results for an individual polling unit.
2. Calculate party vote totals for an LGA using polling-unit results.
3. Add a new polling unit and save its party results.

## Requirements

- Python 3
- MariaDB or MySQL
- The database schema and data in `bincom_test.sql`
- `mysql-connector-python`
- `python-dotenv`

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/meem08/bincom-election-results.git
cd bincom-election-results
```

### 2. Install dependencies

```bash
python3 -m pip install mysql-connector-python python-dotenv
```

### 3. Set up the database

Create the `bincomphptest` database in MariaDB or MySQL, then import the supplied SQL file if the database has not already been populated:

```bash
mariadb -u root -p bincomphptest < bincom_test.sql
```

On Ubuntu systems where MariaDB root authentication uses `sudo`, you may instead use:

```bash
sudo mariadb bincomphptest < bincom_test.sql
```

Do not re-import the SQL file into a database containing work you want to preserve.

### 4. Configure environment variables

Create a `.env` file in the project root:

```dotenv
DB_HOST=localhost
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_NAME=bincomphptest
```


### 5. Run the application

```bash
python3 app.py
```

## Usage

Choose an option from the application menu:

- **Option 1:** Enter a polling unit ID to view its election results.
- **Option 2:** Enter an LGA database ID to calculate party totals from polling-unit results.
- **Option 3:** Select an LGA and ward, enter polling-unit details and party scores, and save the records.

## Security

Database credentials are stored in `.env`, which should be excluded from version control through `.gitignore`.
