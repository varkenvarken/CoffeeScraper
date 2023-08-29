from coffeescraper.html import generate_graph_html
from datetime import datetime

import pathlib

class TestHTML:
    def test_basic(self):
        data = (
            (1, "url1", 7.21, datetime(2021, 8, 8)),
            (2, "url2", 7.31, datetime(2021, 8, 8)),
        )
        p = pathlib.Path('/tmp/graph.html')
        p.unlink(missing_ok=True)
        generate_graph_html(data,"url1",7.21,p)
        assert p.exists()
        
