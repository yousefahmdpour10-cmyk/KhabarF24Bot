"""
KhabarF24 Database Module v8.0
Supabase PostgreSQL - Enhanced Deduplication
"""

import os
import time
import logging
from typing import Optional, Tuple

import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    logger.warning("DATABASE_URL environment variable is not set!")


def get_connection():
    """Create and return database connection"""
    return psycopg2.connect(
        DATABASE_URL,
        sslmode="require",
        connect_timeout=15,
        cursor_factory=RealDictCursor
    )


def execute_with_retry(query: str, params=None, fetch: bool = False, max_attempts: int = 3):
    """Execute query with retry mechanism"""
    for attempt in range(1, max_attempts + 1):
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute(query, params or ())

            if fetch:
                result = cursor.fetchone()
            else:
                result = None

            conn.commit()
            return result

        except Exception as e:
            logger.error(f"Database error (attempt {attempt}/{max_attempts}): {e}")
            if conn:
                try:
                    conn.rollback()
                except:
                    pass
            if attempt < max_attempts:
                time.sleep(2 ** attempt)  # Exponential backoff
            continue

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    return None


def init_db():
    """Initialize database tables"""
    execute_with_retry(
        """
        CREATE TABLE IF NOT EXISTS published_news (
            id SERIAL PRIMARY KEY,
            link TEXT UNIQUE NOT NULL,
            title TEXT,
            source TEXT,
            category TEXT,
            published_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )
    logger.info("✅ Database initialized successfully (Supabase PostgreSQL)")


def is_published(link: str, title: str = None) -> bool:
    """Check if news is already published (link or title fallback)"""
    if not link and not title:
        return False

    try:
        # Check by link first
        if link:
            result = execute_with_retry(
                "SELECT 1 FROM published_news WHERE link = %s",
                (link,),
                fetch=True
            )
            if result:
                logger.debug(f"Duplicate by link: {link[:80]}...")
                return True

        # Fallback: Check by title (if link not reliable)
        if title:
            result = execute_with_retry(
                "SELECT 1 FROM published_news WHERE title = %s",
                (title,),
                fetch=True
            )
            if result:
                logger.debug(f"Duplicate by title: {title[:70]}...")
                return True

        return False

    except Exception as e:
        logger.error(f"Error in is_published: {e}")
        return False  # در صورت خطا اجازه بده خبر پردازش بشه


def mark_as_published(link: str, title: str = None, source: str = None, category: str = None):
    """Mark news as published"""
    try:
        execute_with_retry(
            """
            INSERT INTO published_news (link, title, source, category, published_at)
            VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
            ON CONFLICT(link) DO NOTHING
            """,
            (link, title, source, category)
        )
        logger.info(f"📝 Marked as published: {title[:70] if title else link[:80]}...")
        
    except Exception as e:
        logger.error(f"Failed to mark as published: {e}")


# Optional: Cleanup old records (optional)
def cleanup_old_records(days: int = 30):
    """Remove old records to keep database clean"""
    try:
        execute_with_retry(
            "DELETE FROM published_news WHERE published_at < NOW() - INTERVAL '%s days'",
            (days,)
        )
        logger.info(f"Cleaned records older than {days} days")
    except Exception as e:
        logger.error(f"Cleanup failed: {e}")
