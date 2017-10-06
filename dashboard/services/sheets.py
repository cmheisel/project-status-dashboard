from __future__ import unicode_literals
from builtins import str

import csv
import io

from collections import OrderedDict

import gspread
import requests

from oauth2client.service_account import ServiceAccountCredentials


class Row(OrderedDict):
    def __init__(self, *args, **kwargs):
        super(Row, self).__init__(*args, **kwargs)
        self.xtras = {}


def load_sheet(sheet_id, sheet_auth_file=""):
    """
    Accepts Google sheet ID, returns a iterator of ordered dictionaries.
    The order reflects the key order in the sheet.
    """
    if not sheet_auth_file:
        return _load_via_csv(sheet_id)
    return _load_via_api(sheet_id, sheet_auth_file)


def _load_via_api(sheet_id, sheet_auth_file):
    credentials = ServiceAccountCredentials.from_json_keyfile_name(sheet_auth_file, ['https://spreadsheets.google.com/feeds'])
    sheetapi = gspread.authorize(credentials)
    worksheet = sheetapi.open_by_key(sheet_id).get_worksheet(0)
    csv = worksheet.export(format='csv')
    return parse_csv(csv.decode("utf-8"))


def _load_via_csv(sheet_id):
    r = requests.get('https://docs.google.com/spreadsheets/d/{}/pub?output=csv'.format(sheet_id))
    return parse_csv(r.text)


def parse_csv(csv_text):
    csv_text = str(csv_text)
    c = csv.reader(io.StringIO(csv_text))
    rows = [row for row in c]
    keys = rows.pop(0)
    normal_keys = [k for k in keys if not k.startswith('_')]

    dict_rows = []
    for row in rows:
        d = Row()
        for i in range(0, len(keys)):
            if keys[i] in normal_keys:
                d[keys[i]] = row[i]
            else:
                d.xtras[keys[i]] = row[i]

        dict_rows.append(d)
    return dict_rows
