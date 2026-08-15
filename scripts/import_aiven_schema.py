import os
import re
from pathlib import Path

import pymysql
from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "Database" / "schema.sql"
ENV_PATH = ROOT / "Backend" / "api" / ".env"

TABLE_ORDER = [
    "eventdetails",
    "skills",
    "states",
    "usercredentials",
    "userprofile",
    "notifications",
    "required_skills",
    "volunteer_availability",
    "volunteer_skills",
    "volunteerhistory",
    "verification_codes",
]


def table_name(statement):
    match = re.search(r"CREATE TABLE\s+(?:`?[^`\s]+`?\.)?`?([^`\s(]+)`?", statement, re.I)
    return match.group(1).lower() if match else ""


def load_statements():
    raw = SCHEMA_PATH.read_text(encoding="utf-8")
    raw = re.sub(r"^CREATE DATABASE[^;]+;\s*", "", raw, flags=re.I | re.M)
    raw = re.sub(r"^USE\s+[^;]+;\s*", "", raw, flags=re.I | re.M)
    raw = raw.replace("volunteermgnt.", "")
    raw = re.sub(r"\bCREATE TABLE\b", "CREATE TABLE IF NOT EXISTS", raw, flags=re.I)

    statements = [statement.strip() for statement in raw.split(";") if statement.strip()]
    return sorted(
        statements,
        key=lambda statement: (
            TABLE_ORDER.index(table_name(statement))
            if table_name(statement) in TABLE_ORDER
            else 999
        ),
    )


def main():
    load_dotenv(ENV_PATH)

    connection = pymysql.connect(
        host=os.environ["MYSQL_HOST"],
        port=int(os.environ["MYSQL_PORT"]),
        user=os.environ["MYSQL_USER"],
        password=os.environ["MYSQL_PASSWORD"],
        db=os.environ["MYSQL_DB"],
        ssl={"ca": os.environ["MYSQL_SSL_CA"]},
    )

    try:
        with connection.cursor() as cursor:
            cursor.execute("SET FOREIGN_KEY_CHECKS=0")
            for statement in load_statements():
                cursor.execute(statement)
            cursor.execute("SET FOREIGN_KEY_CHECKS=1")
            connection.commit()

            cursor.execute("SHOW TABLES")
            tables = sorted(row[0] for row in cursor.fetchall())
            print(f"created_tables={len(tables)}")
            print(",".join(tables))
    finally:
        connection.close()


if __name__ == "__main__":
    main()
