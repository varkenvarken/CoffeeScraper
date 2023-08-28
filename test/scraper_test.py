import pytest

from coffeescraper.scraper import CoffeeScraper

def test_CoffeeScraper():
    cd = CoffeeScraper("http://webserver", r"<span.*>(?P<price>.*)</span>")
    result = cd()
    assert result[1] == 3.66
