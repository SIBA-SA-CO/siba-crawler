import pytest
from src.scrapers.rushprime.parserushprimecsv import parseRushPrimeCsv

def test_parser_valid_csv():
    content = b"Program Start Date,Program Start Time,Program Title,Program Description\n07/29/2025,18:00,Title 1,Desc 1"
    df = parseRushPrimeCsv(content)

    assert not df.empty
    assert list(df.columns) == ["Program Start Date", "Program Start Time", "Program Title", "Program Description"]
    assert df.iloc[0]["Program Title"] == "Title 1"
