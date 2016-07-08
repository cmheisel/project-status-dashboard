from __future__ import unicode_literals
from builtins import str

import csv
import io

from collections import OrderedDict

import requests


class Row(OrderedDict):
    def __init__(self, *args, **kwargs):
        super(Row, self).__init__(*args, **kwargs)
        self.xtras = {}


def load_sheet(sheet_id):
    """
    Accepts Google sheet ID, returns a iterator of ordered dictionaries.
    The order reflects the key order in the sheet.
    """
    r = requests.get('https://docs.google.com/spreadsheets/d/{}/pub?output=csv'.format(sheet_id))
    return parse_csv(r.text)


def parse_csv(csv_text):
    c = csv.reader(io.StringIO(str(csv_text)))
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
