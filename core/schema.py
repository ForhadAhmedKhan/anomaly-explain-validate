from dataclasses import dataclass
import pandas as pd

REQUIRED_COLUMNS = ["timestamp", "asset_id", "sensor", "value"]

@dataclass
class Dataset:
      name: str
      is_synthetic: bool
      readings: pd.DataFrame  # columns: REQUIRED_COLUMNS

      def validate(self) -> None:
          missing = set(REQUIRED_COLUMNS) - set(self.readings.columns)
          if missing:
              raise ValueError(f"Missing columns: {missing}")