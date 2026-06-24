# Claims Data Quality Pipeline

This project is a small ETL/data quality pipeline built with Python, AWS S3, and PostgreSQL.

## What it does

- Reads raw insurance claims data from AWS S3
- Validates records using business rules
- Loads valid claims into PostgreSQL
- Stores rejected records with rejection reasons
- Provides SQL reports for claims analysis

## Validation Rules

A claim is rejected if:

- claim_id is missing
- claim_id is duplicated
- member_id is missing
- provider_id is missing
- claim_date is invalid
- claim_date is in the future
- claim_amount is less than or equal to zero
- status is not APPROVED, DENIED, or PENDING

## Tech Stack

- Python
- Pandas
- boto3
- PostgreSQL
- AWS S3
- SQL

## Example Business Reports

- Total claims by status
- Total claim amount by provider
- Rejected claims by reason
- Daily approved claims total

## Steps to run the program
- Create a `.env` file from the `.env.example` file given
- Fill out the `.env` file with actual credentials
- python -m venv venv
- pip install -r requirements.txt
- psql -h localhost -U postgres -d claims_db -f sql/schema.sql
- python ./src/run.py
- psql -h localhost -U postgres -d claims_db -f sql/reports.sql