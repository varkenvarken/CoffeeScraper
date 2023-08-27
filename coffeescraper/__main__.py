# SPDX-License-Identifier: GPL-3.0-or-later

# coffeescraper (c) 2023 Michel Anders (varkenvarken)
#
# coffeescraper is an experiment in webscraping both with and without Selenium

from .scraper import sites
from .database import insert_tuple_into_table, get_prices, get_difference
from .spreadsheet import write_sheet
from .html import generate_graph_html
from .sftp import upload_file_via_sftp
from .smtp import send_message
from .utils import get_env, get_secret_file

# TODO: improve the chart in the HTML output
# TODO: improve the excel sheet (table headers)
# TODO: do proper logging across all module
# TODO: refactor database module into proper class

if __name__ == "__main__":
    filename = "/tmp/coffeescraper.xlsx"
    filename_html = "/tmp/coffeescraper.html"
    for site in sites:
        result = site()
        print(result)
        insert_tuple_into_table(*result)

    write_sheet(get_prices(), filename=filename)
    print(f"spreadsheet saved as {filename}")

    generate_graph_html(get_prices(), filename=filename_html)
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
    if get_difference() <= -limit:
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
