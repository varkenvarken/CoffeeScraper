# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Generator
from datetime import datetime
import psycopg2

class PriceDatabase:
    """
    A class for managing a PostgreSQL database of coffee prices.

    This class provides methods to create the necessary table, insert price data,
    retrieve price data, and calculate the price difference between two days.

    Attributes:
        connection (psycopg2.extensions.connection): The database connection.
        table_created (bool): Flag indicating if the table has been created.

    Methods:
        __init__(self, host, port, username, password, dbname):
            Initializes a PriceDatabase instance with database connection parameters.
        get_password() -> str:
            Static method to retrieve the database password from a secrets file.
        create_table(self) -> None:
            Creates the 'url_price' table if it doesn't exist.
        insert_tuple_into_table(self, url, price) -> None:
            Inserts a tuple of URL, price, and timestamp into the database.
        get_prices(self) -> Generator[tuple[int, str, float, datetime], None, None]:
            Retrieves all rows from the 'url_price' table as a generator of tuples.
        get_difference(self) -> float:
            Calculates the price difference between minimum prices of today and yesterday.

    """
   
    def __init__(self, host:str="db", port:str="5432", username:str="postgres", password:str|None="postgres", dbname:str="postgres"):
        """
        Initialize a PriceDatabase instance with the given database connection parameters.

        Args:
            host (str): Database host name.
            port (str): Database port number.
            username (str): Database username.
            password (str | None): Database password or None to read from secrets file.
            dbname (str): Database name.
        """
        self.connection = psycopg2.connect(
            dbname=dbname,
            user=username,
            password=password if password is not None else self.get_password(),
            host=host,
            port=port,
        )
        self.table_created = False
    
    @staticmethod
    def get_password() -> str:
        """
        Retrieve the database password from a secrets file.

        It tries to read /run/secrets/postgres-password but if
        it fails, it returns "postgres", which is the default
        password used in many test/dev postgres containers.

        Returns:
            str: The retrieved database password.
        """
        try:
            with open("/run/secrets/postgres-password") as f:
                return f.readline().strip()
        except FileNotFoundError:
            return "postgres"


    def create_table(self) -> None:
        create_table_query = """
            CREATE TABLE IF NOT EXISTS url_price (
                id SERIAL PRIMARY KEY,
                url TEXT,
                price FLOAT,
                timestamp TIMESTAMP
            );
        """
        with self.connection.cursor() as cursor:
            cursor.execute(create_table_query)
            self.connection.commit()
            self.table_created = True


    def insert_tuple_into_table(self, url:str, price:float) -> None:
        """
        Insert a tuple of URL, price, and timestamp into the database.

        The timestamp added to the record is the current time.

        Args:
            url (str): The URL associated with the price.
            price (float): The price value to be inserted.

        Returns:
            None
        """
        
        if not self.table_created: self.create_table()

        with self.connection.cursor() as cursor:
            timestamp = datetime.now()
            insert_query = """
                INSERT INTO url_price (url, price, timestamp)
                VALUES (%s, %s, %s);
            """
            cursor.execute(insert_query, (url, price, timestamp))
            self.connection.commit()
            print("Tuple inserted successfully!")


    def get_prices(self) -> Generator[tuple[int,str,float,datetime],None,None]:
        """
        Retrieve all rows from the 'url_price' table as a generator of tuples.

        Yields:
            tuple[int, str, float, datetime]: Generator yielding rows with id, url, price, and timestamp.

        Returns:
            Generator[tuple[int, str, float, datetime], None, None]
        """
        
        if not self.table_created: self.create_table()

        with self.connection.cursor() as cursor:
            query = """
                SELECT * FROM url_price;
            """
            cursor.execute(query)
            for row in cursor.fetchall():
                yield row


    def get_difference(self) -> float:
        """
        Return the price difference between the minimum prices of today and yesterday.

        If the result is negative this means the price is lower today than it was yesterday.

        Returns:
            float: The price difference between today and yesterday.
        """
        if not self.table_created: self.create_table()

        with self.connection.cursor() as cursor:
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

