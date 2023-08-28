import pytest

from coffeescraper.scraper import CoffeeScraper,ChromiumCoffeeScraper,PricePattern
from selenium.webdriver.common.by import By

class TestCoffeeScraper:
    def test_basic(self):
        url = "http://webserver"
        cd = CoffeeScraper(url, r'<span\s+class="price">(?P<price>.*)</span>')
        result = cd()
        assert result[0] == url
        assert result[1] == 3.66

    def test_conversion(self):
        url = "http://webserver"
        cd = CoffeeScraper(url, r'<span\s+class="comma-price">(?P<price>.*)</span>',lambda x: x.replace(",", "."))
        result = cd()
        assert result[0] == url
        assert result[1] == 3.66

class TestChromiumCoffeeScraper:
    def test_basic(self):
        url = "http://webserver"
        cd = ChromiumCoffeeScraper(url, PricePattern(By.CLASS_NAME,"price"))
        result = cd()
        assert result[0] == url
    
    def test_conversion(self):
        url = "http://webserver"
        cd = ChromiumCoffeeScraper(url, PricePattern(By.CLASS_NAME,"price"),lambda x: x.replace(",", "."))
        result = cd()
        assert result[0] == url
        assert result[1] == 3.66