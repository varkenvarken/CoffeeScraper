import pytest
from datetime import datetime

from coffeescraper.database import PriceDatabase

class TestDatabase:
    def test_basic(self):
        db = PriceDatabase()
        assert db is not None

    def test_insert_retrieve(self):
        db = PriceDatabase()
        db.insert_tuple_into_table("myurl",100.0)
        seen = False
        for row in db.get_prices():
            assert type(row[0]) == int
            if row[1] == "myurl":
                seen = True
                assert row[2] == 100.0
            assert type(row[3]) == datetime
        assert seen

    def test_difference(self):
        db = PriceDatabase()
        db.insert_tuple_into_table("myurl",100.0)
        result = db.get_difference()
        assert type(result) == float
