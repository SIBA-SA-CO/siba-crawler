import pandas as pd
from src.scrapers.rushprime.rushprimedataprocessor import RushPrimeDataProcessor

def test_process_data_valid():
    raw = pd.DataFrame([{
        "Program Start Date": "07/29/2025",
        "Program Start Time": "18:00",
        "Program Title": "Some Title",
        "Program Description": "Some Description"
    }])
    
    processor = RushPrimeDataProcessor("UTC")
    result = processor.processData(raw, "Default Desc", "")

    assert isinstance(result, list)
    assert result[0]["title"] == "Some Title"
    assert "date" in result[0]
    assert "hour" in result[0]
    assert "content" in result[0]
