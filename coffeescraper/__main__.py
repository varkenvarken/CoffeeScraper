# SPDX-License-Identifier: GPL-3.0-or-later

# coffeescraper (c) 2023 Michel Anders (varkenvarken)
#
# coffeescraper is an experiment in webscraping both with and without Selenium

import logging

from .scraper import sites
from .database import PriceDatabase
from .spreadsheet import write_sheet
from .html import generate_graph_html
from .sftp import upload_file_via_sftp
from .smtp import send_message
from .utils import get_env, get_secret_file

# TODO: improve the excel sheet (table headers)

if __name__ == "__main__":

    loglevel = get_env("LOGLEVEL","WARNING")
    numeric_level = getattr(logging, loglevel.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % loglevel)
    logging.basicConfig(level=numeric_level, format='%(levelname)s:%(module)s - %(asctime)s %(message)s')

    filename = "/tmp/coffeescraper.xlsx"
    filename_html = "/tmp/coffeescraper.html"

    logging.info("coffeescraper started")

    db = PriceDatabase()

    lowest_price_today = 1000000.0
    cheapest_site = None
    for site in sites:
        result = site()
        db.insert_tuple_into_table(*result)
        if result[1] < lowest_price_today:
            lowest_price_today = result[1]
            cheapest_site = result[0]

    write_sheet(db.get_prices(), filename=filename)

    generate_graph_html(db.get_prices(), cheapest_site=cheapest_site, lowest_price_today=lowest_price_today, filename=filename_html)

    upload_file_via_sftp(
        hostfile="/run/secrets/sftp_host",
        usernamefile="/run/secrets/sftp_user",
        passwordfile="/run/secrets/sftp_password",
        local_file_path=filename,
        remote_file_path=get_env("EXCELREPORT","/coffeescraper.xlsx"),
    )

    upload_file_via_sftp(
        hostfile="/run/secrets/sftp_host",
        usernamefile="/run/secrets/sftp_user",
        passwordfile="/run/secrets/sftp_password",
        local_file_path=filename_html,
        remote_file_path=get_env("HTMLREPORT","/coffeescraper.html"),
    )

    limit = float(get_env("ALERTLIMIT",0.50))
    diff = db.get_difference()
    if  diff <= -limit:
        send_message(
            get_env("ALERTSENDER"),
            get_env("ALERTRECIPIENTS"),
            get_env("ALERTSUBJECT","Coffee Alert"),
            get_secret_file("/run/secrets/smtp_message").format(limit=limit)
        )
    else:
        logging.info(f"no mailing sent, limit not reached {diff} > -{limit}")

    logging.info("coffeescraper completed")
