# SPDX-License-Identifier: GPL-3.0-or-later

import logging
from openpyxl import Workbook


def write_sheet(data, filename="/tmp/coffeescraper.xlsx"):
    wb = Workbook()
    ws = wb.active
    for row in data:
        ws.append(row)
    wb.save(filename)
    logging.info(f"spreadsheet saved to {filename}")
