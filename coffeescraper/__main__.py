# SPDX-License-Identifier: GPL-3.0-or-later

# coffeescraper (c) 2023 Michel Anders (varkenvarken)
#
# coffeescraper is an experiment in webscraping both with and without Selenium

from .scraper import sites
from .database import PriceDatabase
from .spreadsheet import write_sheet
from .html import generate_graph_html
from .sftp import upload_file_via_sftp
from .smtp import send_message
from .utils import get_env, get_secret_file

# TODO: improve the excel sheet (table headers)
# TODO: do proper logging across all module

if __name__ == "__main__":
    filename = "/tmp/coffeescraper.xlsx"
    filename_html = "/tmp/coffeescraper.html"

    db = PriceDatabase()

    lowest_price_today = 1000000.0
    cheapest_site = None
    for site in sites:
        result = site()
        print(result)
        db.insert_tuple_into_table(*result)
        if result[1] < lowest_price_today:
            lowest_price_today = result[1]
            cheapest_site = result[0]

    write_sheet(db.get_prices(), filename=filename)
    print(f"spreadsheet saved as {filename}")

    generate_graph_html(db.get_prices(), cheapest_site=cheapest_site, lowest_price_today=lowest_price_today, filename=filename_html)
    print(f"html graph saved as {filename_html}")

    upload_file_via_sftp(
        hostfile="/run/secrets/sftp_host",
        usernamefile="/run/secrets/sftp_user",
        passwordfile="/run/secrets/sftp_password",
        local_file_path=filename,
        remote_file_path=get_env("EXCELREPORT","/coffeescraper.xlsx"),
    )
    print(f"spreadsheet uploaded to coffeescraper.xlsx")

    upload_file_via_sftp(
        hostfile="/run/secrets/sftp_host",
        usernamefile="/run/secrets/sftp_user",
        passwordfile="/run/secrets/sftp_password",
        local_file_path=filename_html,
        remote_file_path=get_env("HTMLREPORT","/coffeescraper.html"),
    )
    print(f"html graph uploaded to coffeescraper.html")

    limit = float(get_env("ALERTLIMIT",0.50))
    if db.get_difference() <= -limit:
        print("mailing an alert")
        send_message(
            get_env("ALERTSENDER"),
            get_env("ALERTRECIPIENTS"),
            get_env("ALERTSUBJECT","Coffee Alert"),
            get_secret_file("/run/secrets/smtp_message").format(limit=limit)
        )
        print("mailing sent")
    else:
        print("no mailing sent, limit not reached")
