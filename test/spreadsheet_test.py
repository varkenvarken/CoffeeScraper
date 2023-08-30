from coffeescraper.spreadsheet import write_sheet
from datetime import datetime

import pathlib

class TestSpreadsheet:
    def test_basic(self):
        data = (
            (1, "url1", 7.21, datetime(2021, 8, 8)),
            (2, "url2", 7.31, datetime(2021, 8, 8)),
        )
        p = pathlib.Path('/tmp/spreadsheet.xlsx')
        p.unlink(missing_ok=True)
        write_sheet(data,p)
        assert p.exists()