# SPDX-License-Identifier: GPL-3.0-or-later

from datetime import datetime
import psycopg2


def get_password():
    # either get the configured password from a docker secret
    # or fall back on the default password while developing
    # in a docker dev container
    try:
        with open("/run/secrets/postgres-password") as f:
            return f.readline().strip()
    except FileNotFoundError:
        return "postgres"


def opendb(password):
    return psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password=password,
        host="db",
        port="5432",
    )


def create_table(conn):
    create_table_query = """
        CREATE TABLE IF NOT EXISTS url_price (
            id SERIAL PRIMARY KEY,
            url TEXT,
            price FLOAT,
            timestamp TIMESTAMP
        );
    """
    cursor = conn.cursor()
    cursor.execute(create_table_query)
    conn.commit()


def insert_tuple_into_table(url, price):
    password = get_password()

    try:
        conn = opendb(password=password)
        create_table(conn)

        cursor = conn.cursor()
        timestamp = datetime.now()
        insert_query = """
            INSERT INTO url_price (url, price, timestamp)
            VALUES (%s, %s, %s);
        """
        cursor.execute(insert_query, (url, price, timestamp))
        conn.commit()

        print("Tuple inserted successfully!")
    except Exception as e:
        print("Error:", e)

    finally:
        # Close the cursor and connection
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def get_prices():
    password = get_password()

    try:
        conn = opendb(password=password)
        cursor = conn.cursor()
        query = """
            SELECT * FROM url_price;
        """
        cursor.execute(query)
        for row in cursor.fetchall():
            yield row
    except Exception as e:
        print("Error:", e)

    finally:
        # Close the cursor and connection
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def get_difference() -> float:
    """
    Return the price difference between the minimum prices of today and yesterday.

    If the result is negative this means the price is lower today than it was yesterday.
    """
    password = get_password()

    try:
        conn = opendb(password=password)
        cursor = conn.cursor()
        query = """
            SELECT price FROM url_price
            WHERE DATE(timestamp) = CURRENT_DATE
            ORDER BY price ASC
            LIMIT 1;
        """
        cursor.execute(query)
        min_today = cursor.fetchone()
        query = """
            SELECT price FROM url_price
            WHERE DATE(timestamp) = CURRENT_DATE - INTERVAL '1 day'
            ORDER BY price ASC
            LIMIT 1;
        """
        cursor.execute(query)
        min_yesterday = cursor.fetchone()
        if min_today is None or min_yesterday is None:
            return 0.0
        return min_today[0] - min_yesterday[0]
    except Exception as e:
        print("Error:", e)
        return 0.0
    finally:
        # Close the cursor and connection
        if cursor:
            cursor.close()
        if conn:
            conn.close()
