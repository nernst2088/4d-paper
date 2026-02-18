import os
import tempfile
import pandas as pd
from src.agents.data_management.data_ingestion import DataIngestionService

def test_csv_ingestion():
    svc = DataIngestionService()

    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
        df = pd.DataFrame({"x": [1,2,3], "y": [4,5,6]})
        df.to_csv(f.name, index=False)
        path = f.name

    try:
        result = svc._load_data(path)
        assert not result.empty
    finally:
        os.unlink(path)