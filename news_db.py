import sqlite3

DB_NAME = "news.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS published_news (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        link TEXT UNIQUE
    )
    """)

    conn.commit()
    conn.close()


def is_published(link):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT 1 FROM published_news WHERE link=?",
        (link,)
    )

    result = cursor.fetchone()

    conn.close()

    print(f"CHECK: {link} -> {result}")

    return result is not None


def mark_as_published(link):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "INSERT OR IGNORE INTO published_news(link) VALUES(?)",
        (link,)
    )

    conn.commit()

    print(f"SAVED: {link}")

    conn.close()
