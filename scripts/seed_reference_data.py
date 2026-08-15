import os
from pathlib import Path

import pymysql
from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT / "Backend" / "api" / ".env"

STATES = [
    ("Alabama", "AL"),
    ("Alaska", "AK"),
    ("Arizona", "AZ"),
    ("Arkansas", "AR"),
    ("California", "CA"),
    ("Colorado", "CO"),
    ("Connecticut", "CT"),
    ("Delaware", "DE"),
    ("Florida", "FL"),
    ("Georgia", "GA"),
    ("Hawaii", "HI"),
    ("Idaho", "ID"),
    ("Illinois", "IL"),
    ("Indiana", "IN"),
    ("Iowa", "IA"),
    ("Kansas", "KS"),
    ("Kentucky", "KY"),
    ("Louisiana", "LA"),
    ("Maine", "ME"),
    ("Maryland", "MD"),
    ("Massachusetts", "MA"),
    ("Michigan", "MI"),
    ("Minnesota", "MN"),
    ("Mississippi", "MS"),
    ("Missouri", "MO"),
    ("Montana", "MT"),
    ("Nebraska", "NE"),
    ("Nevada", "NV"),
    ("New Hampshire", "NH"),
    ("New Jersey", "NJ"),
    ("New Mexico", "NM"),
    ("New York", "NY"),
    ("North Carolina", "NC"),
    ("North Dakota", "ND"),
    ("Ohio", "OH"),
    ("Oklahoma", "OK"),
    ("Oregon", "OR"),
    ("Pennsylvania", "PA"),
    ("Rhode Island", "RI"),
    ("South Carolina", "SC"),
    ("South Dakota", "SD"),
    ("Tennessee", "TN"),
    ("Texas", "TX"),
    ("Utah", "UT"),
    ("Vermont", "VT"),
    ("Virginia", "VA"),
    ("Washington", "WA"),
    ("West Virginia", "WV"),
    ("Wisconsin", "WI"),
    ("Wyoming", "WY"),
]

SKILLS = [
    ("Administration", "Office and administrative support"),
    ("Animal Care", "Animal handling and shelter support"),
    ("Childcare", "Supervising and supporting children"),
    ("Cleaning", "Cleaning and sanitation support"),
    ("Community Outreach", "Engaging community members"),
    ("Cooking", "Food preparation and kitchen support"),
    ("Counseling", "Emotional support and guidance"),
    ("Data Entry", "Entering and maintaining records"),
    ("Driving", "Transportation and delivery support"),
    ("Education", "Teaching and tutoring support"),
    ("Event Planning", "Planning and coordinating events"),
    ("First Aid", "Basic emergency medical support"),
    ("Fundraising", "Donation and campaign support"),
    ("Graphic Design", "Visual and design support"),
    ("Healthcare", "Health-related volunteer support"),
    ("Heavy Lifting", "Moving supplies and equipment"),
    ("IT Support", "Technology troubleshooting"),
    ("Language Translation", "Translation and interpretation"),
    ("Leadership", "Team lead and coordination support"),
    ("Marketing", "Promotion and communications"),
    ("Mentoring", "One-on-one guidance and support"),
    ("Photography", "Event and program photography"),
    ("Public Speaking", "Speaking to groups or audiences"),
    ("Registration", "Check-in and attendance support"),
    ("Social Media", "Posting and online engagement"),
    ("Sorting Donations", "Sorting and organizing donated goods"),
    ("Tutoring", "Academic support"),
    ("Writing", "Writing and editing support"),
]


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
            cursor.executemany(
                """
                INSERT INTO states (state_name, abbreviation)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE state_name = VALUES(state_name)
                """,
                STATES,
            )

            cursor.executemany(
                """
                INSERT IGNORE INTO skills (skill_name, skill_description)
                VALUES (%s, %s)
                """,
                SKILLS,
            )

            connection.commit()

            cursor.execute("SELECT COUNT(*) FROM states")
            state_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM skills")
            skill_count = cursor.fetchone()[0]

            print(f"states={state_count}")
            print(f"skills={skill_count}")
    finally:
        connection.close()


if __name__ == "__main__":
    main()
