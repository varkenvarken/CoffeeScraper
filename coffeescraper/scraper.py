# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Tuple
from collections import namedtuple
import requests
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By


class PriceNotFoundException(Exception):
    pass


PricePattern = namedtuple("PricePattern", ["by", "value"])


class CoffeeScraper:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
    }

    def __init__(self, url: str, pricepattern: str, format=lambda x: x) -> None:
        self.url = url
        self.pricepattern = (
            re.compile(pricepattern) if pricepattern is not None else None
        )
        self.format = format

    def __call__(self) -> Tuple[str, float] | None:
        response = requests.get(self.url, headers=self.headers)
        if match := re.search(self.pricepattern, response.text):
            return self.url, float(self.format(match.group("price")))
        raise PriceNotFoundException(f"No price found in {self.url}")


class ChromiumCoffeeScraper(CoffeeScraper):
    def __init__(
        self, url: str, pricepattern: PricePattern, format=lambda x: x
    ) -> None:
        super().__init__(url, None, format)
        self.pricepattern = pricepattern
        self.options = Options()
        self.options.add_argument("--headless")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_argument(f"--user-agent={self.headers['User-Agent']}")

    def __call__(self) -> Tuple[str, float] | None:
        driver = webdriver.Chrome(
            service=Service(
                service_args=["--verbose", "--log-path=/tmp/webdriver.log"]
            ),
            options=self.options,
        )

        # TODO: add some timeout handling here
        driver.get(self.url)

        try:
            price = driver.find_element(by=By.CLASS_NAME, value="current-price")
            price = self.url, self.format(price.text)
        except:
            price = None

        driver.close()

        driver.quit()
        return price


koffiehenk = CoffeeScraper(
    url="https://www.koffiehenk.nl/dolce-gusto-lungo-xl",
    pricepattern=r'<meta property="product:price:amount" content="(?P<price>\d+\.\d+)"/>',
)


coffeepoddeals = CoffeeScraper(
    url="https://www.coffeepoddeals.com/capsules-dolce-gusto-lungo-xl",
    pricepattern=r'<meta property="product:price:amount" content="(?P<price>\d+\.\d+)"/>',
)


deprijshamer = CoffeeScraper(
    url="https://www.deprijshamer.nl/koffie/cups/dolce-gusto-lungo-xl",
    pricepattern=r"'value':\s+(?P<price>\d+\.\d+),",
)


dolce_gusto = CoffeeScraper(
    url="https://www.dolce-gusto.nl/koffiesmaken/lungo-xl",
    pricepattern=r'<meta property="product:price:amount" content="(?P<price>\d+\.\d+)"/>',
)


koffievoordeel = CoffeeScraper(
    url="https://www.koffievoordeel.nl/dolce-gusto-capsules-cafe-lungo-xl",
    pricepattern=r'<meta property="bc:current_price" content="(?P<price>\d+\,\d+)"/>',
    format=lambda x: x.replace(",", "."),
)


jumbo = ChromiumCoffeeScraper(
    url="https://www.jumbo.com/producten/nescafe-dolce-gusto-lungo-capsules-30-koffiecups-352850DS",
    pricepattern=PricePattern(by=By.CLASS_NAME, value="current-price"),
    format=lambda x: float(re.sub(r"\s", "", x)) / 100,
)


sites = (
    koffiehenk,
    coffeepoddeals,
    deprijshamer,
    dolce_gusto,
    koffievoordeel,
    jumbo,
)
