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
    mocker.spy(sheets, '_load_via_csv')
    mocker.spy(sheets, '_load_via_api')

    sheets.load_sheet("FOOBARBAZ")
    assert sheets._load_via_csv.call_count == 1
    assert sheets._load_via_api.call_count == 0


def test_load_sheet_api_if_auth_provided(sheets, mocker):
    mock_sheetapi = mocker.Mock()
    mock_spreadsheet = mocker.Mock()
    mock_spreadsheet.get_worksheet.return_value

    mock_sheetapi.open_by_key.return_value = mock_spreadsheet

    mock_authorize = mocker.Mock()
    mock_authorize.return_value = mock_sheetapi

    mocker.patch.object(sheets, 'ServiceAccountCredentials')

    mocker.patch('gspread.authorize', mock_sheetapi)

    mocker.spy(sheets, '_load_via_csv')
    mocker.spy(sheets, '_load_via_api')

    args = ("FOOBARBAZ", "dashboard/tests/fake_google_client_secret.json")
    sheets.load_sheet(*args)
    assert sheets._load_via_csv.call_count == 0
    sheets._load_via_api.assert_called_once_with(*args)
