import pytest
from pytest_mock import MockerFixture

from datetime import datetime
import psycopg2

from coffeescraper.database import PriceDatabase


def clean_table(conn):
    clean_table_query = "DELETE FROM url_price;"
    with conn.cursor() as cursor:
        cursor.execute(clean_table_query)
        conn.commit()


class TestDatabase:
    def test_basic(self):
        db = PriceDatabase()
        assert db is not None

    def test_insert_retrieve(self):
        db = PriceDatabase()
        db.insert_tuple_into_table("myurl", 100.0)
        seen = False
        for row in db.get_prices():
            assert type(row[0]) == int
            if row[1] == "myurl":
                seen = True
                assert row[2] == 100.0
            assert type(row[3]) == datetime
        assert seen

    def test_difference(self, mocker: MockerFixture):
        db = PriceDatabase()
        clean_table(db.connection)

        mocker.patch("coffeescraper.database.now", return_value=datetime(2011, 8, 8))
        db.insert_tuple_into_table("myurl", 100.0)
        mocker.patch("coffeescraper.database.now", return_value=datetime(2011, 8, 9))
        db.insert_tuple_into_table("myurl", 100.0)
        result = db.get_difference()
        assert type(result) == float
        assert result == 0.0