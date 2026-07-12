import os
import psycopg2
from psycopg2 import sql


DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    return psycopg2.connect(DATABASE_URL)


def init_db():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS published_news (
        id SERIAL PRIMARY KEY,
        link TEXT UNIQUE
    )
    """)

    conn.commit()
    cursor.close()
    conn.close()

    print("✅ PostgreSQL database ready.")


def is_published(link):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT 1 FROM published_news WHERE link=%s",
        (link,)
    )

    result = cursor.fetchone()

    cursor.close()
    conn.close()

    print(f"CHECK: {link} -> {result}")

    return result is not None


def mark_as_published(link):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO published_news(link)
        VALUES(%s)
        ON CONFLICT(link) DO NOTHING
        """,
        (link,)
    )

    conn.commit()

    cursor.close()
    conn.close()

    print(f"SAVED: {link}")
