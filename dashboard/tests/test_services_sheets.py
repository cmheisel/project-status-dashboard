import pytest


@pytest.fixture
def sheets():
    from ..services import sheets
    return sheets


def test_setup(sheets):
    assert sheets


def test_order_of_columns(sheets):
    csv = u"""Key1,Key2,Key3,Key4
Value1A,Value2A,Value3A,Value4A
Value1B,Value2B,Value3B,Value4B"""
    results = sheets.parse_csv(csv)
    expected_keys = ["Key1", "Key2", "Key3", "Key4"]
    actual_keys = [key for key in results[0].keys()]
    assert expected_keys == actual_keys


def test_order_of_rows(sheets):
    csv = u"""Key1,Key2,Key3,Key4
Value1A,Value2A,Value3A,Value4A
Value1B,Value2B,Value3B,Value4B"""
    results = sheets.parse_csv(csv)
    assert results[0]['Key1'] == 'Value1A'
    assert results[1]['Key1'] == 'Value1B'


def test_special_attributes(sheets):
    csv = u"""Key1,Key2,Key3,Key4,_special_key1,_amazing_key2
Value1A,Value2A,Value3A,Value4A,,
Value1B,Value2B,Value3B,Value4B,SValue5B,SValue6B"""
    results = sheets.parse_csv(csv)
    assert '_special_key1' not in results[0].keys()
    assert '_amazing_key2' not in results[0].keys()

    assert results[0].xtras['_special_key1'] is ''
    assert results[0].xtras['_amazing_key2'] is ''
    assert results[1].xtras['_special_key1'] == "SValue5B"
    assert results[1].xtras['_amazing_key2'] == "SValue6B"


def test_load_sheet_uses_csv_if_auth_arg_is_empty(sheets, mocker):
    sheets._load_via_csv = mocker.Mock()
    sheets._load_via_api = mocker.Mock()

    sheets.load_sheet("FOOBARBAZ")
    assert sheets._load_via_csv.call_count == 1
    assert sheets._load_via_api.call_count == 0


def test_load_sheet_api_if_auth_provided(sheets, mocker):
    sheets._load_via_csv = mocker.Mock()
    sheets._load_via_api = mocker.Mock()

    args = ("FOOBARBAZ", "google_client_secret.json")
    sheets.load_sheet(*args)
    assert sheets._load_via_csv.call_count == 0
    assert sheets._load_via_api.call_count == 1
    assert sheets._load_via_api.called_with(*args)
