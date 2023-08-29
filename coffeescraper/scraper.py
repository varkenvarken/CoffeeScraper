# SPDX-License-Identifier: GPL-3.0-or-later

import logging
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

# a PricePattern tuple should be passed as an argument to a
# ChromiumCoffeeScraper constructor.
# It is used to locate the element inside a page that contains
# the price information.
# It consists of a by attribute that specified the type of item
# to look for, for example, By.CLASS_NAME, and a value attribute
# # that specifies the actual element, for example. "current-price"
PricePattern = namedtuple("PricePattern", ["by", "value"])


class CoffeeScraper:
    """
    A class for scraping coffee-related information from a given URL.

    This class provides functionality to scrape coffee-related information, particularly prices,
    from a specified URL using a regular expression pattern. It sends an HTTP GET request with
    custom headers to the given URL and attempts to extract the coffee price using the provided
    price pattern.

    Attributes:
        headers (dict): Default User-Agent headers for the HTTP request.
        
    Args:
        url (str): The URL from which to scrape the coffee-related information.
        pricepattern (str): A regular expression pattern used to extract the coffee price.
        format (function, optional): A function to format the extracted price (default is identity function).

    Methods:
        __init__(self, url: str, pricepattern: str, format=lambda x: x) -> None:
            Initializes a CoffeeScraper instance with the provided URL, price pattern, and format function.
        
        __call__(self) -> Tuple[str, float] | None:
            Calls the instance and performs the scraping. Returns a tuple containing the URL and the extracted
            coffee price if successful, or raises PriceNotFoundException if no price is found.
    """
        
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
    }

    def __init__(self, url: str, pricepattern: str, format=lambda x: x) -> None:
        """
        Initialize a CoffeeScraper instance.
        
        Args:
            url (str): The URL from which to scrape the coffee-related information.
            pricepattern (str): A regular expression pattern used to extract the coffee price.
            format (function, optional): A function to format the extracted price (default is identity function).
        """
        self.url = url
        self.pricepattern = (
            re.compile(pricepattern) if pricepattern is not None else None
        )
        self.format = format

    def __call__(self) -> Tuple[str, float] | None:
        """
        Perform the scraping and extraction of coffee-related information.
        
        Returns:
            Tuple[str, float] | None: A tuple containing the URL and the extracted coffee price if successful.
                                      Returns None if no price is found.
        
        Raises:
            PriceNotFoundException: If no price is found in the scraped content.
        """
        response = requests.get(self.url, headers=self.headers, timeout=15.0)
        logging.debug(f"{self.url} {response.status_code}:{response.reason}")
        if match := re.search(self.pricepattern, response.text):
            try:
                price = match.group("price")
                price = float(self.format(price))
                logging.info(f"price from {self.url} = {price}")
            except ValueError:
                raise PriceNotFoundException(f"could not convert {price} to float in {self.url}")
            return self.url, price
        raise PriceNotFoundException(f"No price found in {self.url}")


class ChromiumCoffeeScraper(CoffeeScraper):
    """
    A derived class for scraping coffee-related information from a given URL using Chromium WebDriver.
    
    This class inherits from CoffeeScraper and extends its functionality by utilizing the Chromium WebDriver
    to perform the scraping. It sends an HTTP GET request to the given URL using the headless Chromium browser,
    then attempts to locate and extract the coffee price from the loaded page.

    Args:
        url (str): The URL from which to scrape the coffee-related information.
        pricepattern (PricePattern): A PricePattern object used to extract the coffee price.
        format (function, optional): A function to format the extracted price (default is identity function).

    Methods:
        __init__(self, url: str, pricepattern: PricePattern, format=lambda x: x) -> None:
            Initializes a ChromiumCoffeeScraper instance with the provided URL, PricePattern, and format function.

        __call__(self) -> Tuple[str, float] | None:
            Calls the instance and performs the scraping using Chromium WebDriver.
            Returns a tuple containing the URL and the extracted coffee price if successful,
            or None if no price is found.
    """
        
    def __init__(
        self, url: str, pricepattern: PricePattern, format=lambda x: x
    ) -> None:
        """
        Initialize a ChromiumCoffeeScraper instance.
        
        Args:
            url (str): The URL from which to scrape the coffee-related information.
            pricepattern (PricePattern): A PricePattern object used to extract the coffee price.
            format (function, optional): A function to format the extracted price (default is identity function).
        """
        
        super().__init__(url, None, format)
        self.pricepattern = pricepattern
        self.options = Options()
        self.options.add_argument("--headless")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_argument(f"--user-agent={self.headers['User-Agent']}")

    def __call__(self) -> Tuple[str, float] | None:
        """
        Perform the scraping and extraction of coffee-related information using Chromium WebDriver.
        
        Returns:
            Tuple[str, float] | None: A tuple containing the URL and the extracted coffee price if successful.
                                     Returns None if no price is found.
        """

        driver = webdriver.Chrome(
            service=Service(
                service_args=["--verbose", "--log-path=/tmp/webdriver.log"]
            ),
            options=self.options,
        )

        driver.implicitly_wait(15);

        driver.get(self.url)

        try:
            price = driver.find_element(self.pricepattern.by, self.pricepattern.value)
            formattedprice = float(self.format(price.text))
            price = self.url, formattedprice
            logging.info(f"price from {self.url} = {formattedprice}")
        except:
            logging.warning(f"{self.url} no element with {self.pricepattern.by} = {self.pricepattern.value} found")
            raise PriceNotFoundException(f"{self.url} no element with {self.pricepattern.by} = {self.pricepattern.value} found")

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
