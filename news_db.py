import os
import psycopg2
import time


DATABASE_URL = os.getenv("DATABASE_URL")



def get_connection():

    return psycopg2.connect(
        DATABASE_URL,
        sslmode="require",
        connect_timeout=10
    )



def execute_with_retry(query, params=None, fetch=False):

    attempts = 3


    for attempt in range(attempts):

        conn = None
        cursor = None


        try:

            conn = get_connection()

            cursor = conn.cursor()


            cursor.execute(
                query,
                params
            )


            if fetch:

                result = cursor.fetchone()

            else:

                result = None


            conn.commit()


            return result



        except Exception as e:


            print(
                f"Database error ({attempt+1}/{attempts}): {e}"
            )


            time.sleep(2)



        finally:

            if cursor:

                cursor.close()


            if conn:

                conn.close()



    return None





def init_db():


    execute_with_retry(
        """
        CREATE TABLE IF NOT EXISTS published_news (
            id SERIAL PRIMARY KEY,
            link TEXT UNIQUE
        )
        """
    )


    print("✅ PostgreSQL database ready.")





def is_published(link):


    result = execute_with_retry(
        """
        SELECT 1 
        FROM published_news 
        WHERE link=%s
        """,
        (link,),
        fetch=True
    )


    print(
        f"CHECK: {link} -> {result}"
    )


    return result is not None





def mark_as_published(link):


    execute_with_retry(
        """
        INSERT INTO published_news(link)
        VALUES(%s)
        ON CONFLICT(link) DO NOTHING
        """,
        (link,)
    )


    print(
        f"SAVED: {link}"
    )
