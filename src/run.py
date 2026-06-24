import os
from datetime import datetime, date
from io import StringIO

import boto3
import pandas as pd
import psycopg2
from dotenv import load_dotenv


load_dotenv()


VALID_STATUSES = {"APPROVED", "DENIED", "PENDING"}


def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
    )


def download_claims_from_s3():
    bucket = os.getenv("AWS_BUCKET_NAME")
    key = os.getenv("AWS_OBJECT_KEY")

    s3 = boto3.client("s3")
    response = s3.get_object(Bucket=bucket, Key=key)

    csv_content = response["Body"].read().decode("utf-8")
    return pd.read_csv(StringIO(csv_content))


def validate_claim(row, seen_claim_ids):
    claim_id = str(row.get("claim_id", "")).strip()
    member_id = str(row.get("member_id", "")).strip()
    provider_id = str(row.get("provider_id", "")).strip()
    claim_date_raw = str(row.get("claim_date", "")).strip()
    claim_amount_raw = row.get("claim_amount")
    status = str(row.get("status", "")).strip().upper()

    if not claim_id:
        return False, "Missing claim_id"

    if claim_id in seen_claim_ids:
        return False, "Duplicate claim_id"

    if not member_id or member_id.lower() == "nan":
        return False, "Missing member_id"

    if not provider_id or provider_id.lower() == "nan":
        return False, "Missing provider_id"

    try:
        parsed_date = datetime.strptime(claim_date_raw, "%Y-%m-%d").date()
        if parsed_date > date.today():
            return False, "Claim date is in the future"
    except ValueError:
        return False, "Invalid claim_date"

    try:
        claim_amount = float(claim_amount_raw)
        if claim_amount <= 0:
            return False, "Claim amount must be greater than zero"
    except ValueError:
        return False, "Invalid claim_amount"

    if status not in VALID_STATUSES:
        return False, "Invalid status"

    return True, None


def load_data(df):
    conn = get_db_connection()
    cursor = conn.cursor()

    seen_claim_ids = set()
    clean_count = 0
    rejected_count = 0

    for _, row in df.iterrows():
        is_valid, reason = validate_claim(row, seen_claim_ids)

        claim_id = str(row.get("claim_id", "")).strip()
        member_id = str(row.get("member_id", "")).strip()
        provider_id = str(row.get("provider_id", "")).strip()
        claim_date = str(row.get("claim_date", "")).strip()
        claim_amount = str(row.get("claim_amount", "")).strip()
        status = str(row.get("status", "")).strip().upper()
        diagnosis_code = str(row.get("diagnosis_code", "")).strip()

        if is_valid:
            cursor.execute(
                """
                INSERT INTO claims (
                    claim_id,
                    member_id,
                    provider_id,
                    claim_date,
                    claim_amount,
                    status,
                    diagnosis_code
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (claim_id) DO NOTHING;
                """,
                (
                    claim_id,
                    member_id,
                    provider_id,
                    claim_date,
                    claim_amount,
                    status,
                    diagnosis_code,
                ),
            )

            seen_claim_ids.add(claim_id)
            clean_count += 1

        else:
            cursor.execute(
                """
                INSERT INTO rejected_claims (
                    claim_id,
                    member_id,
                    provider_id,
                    claim_date,
                    claim_amount,
                    status,
                    diagnosis_code,
                    rejection_reason
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
                """,
                (
                    claim_id,
                    member_id,
                    provider_id,
                    claim_date,
                    claim_amount,
                    status,
                    diagnosis_code,
                    reason,
                ),
            )

            rejected_count += 1

    conn.commit()
    cursor.close()
    conn.close()

    print(f"Loaded clean records: {clean_count}")
    print(f"Rejected records: {rejected_count}")


def main():
    print("Downloading claims file from S3...")
    df = download_claims_from_s3()

    print("Validating and loading claims into PostgreSQL...")
    load_data(df)

    print("Pipeline completed.")


if __name__ == "__main__":
    main()