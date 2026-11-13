import pandas as pd
import pytest
from core.schema import Dataset

def test_valid_dataset_passes():
      df = pd.DataFrame(
          {"timestamp": [0], "asset_id": ["A1"], "sensor": ["pressure"], "value": [1.0]}
      )
      Dataset("demo", True, df).validate()

def test_missing_column_fails():
      df = pd.DataFrame({"timestamp": [0], "value": [1.0]})
      with pytest.raises(ValueError):
          Dataset("demo", True, df).validate()