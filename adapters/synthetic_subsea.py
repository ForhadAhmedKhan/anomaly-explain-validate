import json
from pathlib import Path

import numpy as np
import pandas as pd

from core.schema import Dataset

POINTS_PER_DAY = 144  # one reading every 10 minutes

SENSORS = {
      "pressure": {"base": 200.0, "daily_amp": 5.0, "noise": 1.0},
      "temperature": {"base": 4.0, "daily_amp": 0.5, "noise": 0.1},
      "vibration": {"base": 2.0, "daily_amp": 0.2, "noise": 0.1},
  }

  # (sensor, type, start_index, length, magnitude)
PLAN = [
      ("vibration", "spike", 600, 3, 3.0),
      ("pressure", "spike", 900, 3, 25.0),
      ("temperature", "spike", 1500, 3, 2.5),
      ("vibration", "flatline", 1900, 50, None),
      ("pressure", "drift", 2500, 400, 30.0),
      ("temperature", "flatline", 2800, 60, None),
      ("vibration", "spike", 3200, 4, 4.0),
      ("temperature", "drift", 3500, 300, 3.0),
      ("pressure", "dropout", 3800, 12, None),
  ]


def build(seed=42, days=30, asset_id="SUBSEA-01"):
      rng = np.random.default_rng(seed)
      ts = pd.date_range("2026-01-01", periods=days * POINTS_PER_DAY, freq="10min")
      t = np.arange(len(ts))

      series = {}
      for sensor, cfg in SENSORS.items():
          daily = cfg["daily_amp"] * np.sin(2 * np.pi * t / POINTS_PER_DAY)
          noise = rng.normal(0, cfg["noise"], len(ts))
          series[sensor] = cfg["base"] + daily + noise

      truth = []
      for i, (sensor, kind, start, length, mag) in enumerate(PLAN, start=1):
          v = series[sensor]
          end = start + length
          if kind == "spike":
              v[start:end] += mag
          elif kind == "drift":
              v[start:end] += np.linspace(0, mag, length)
          elif kind == "flatline":
              v[start:end] = v[start]
          elif kind == "dropout":
              v[start:end] = np.nan
          truth.append({
              "id": f"A{i:03d}",
              "asset_id": asset_id,
              "sensor": sensor,
              "type": kind,
              "start": str(ts[start]),
              "end": str(ts[end - 1]),
              "magnitude": mag,
          })

      frames = [
          pd.DataFrame({"timestamp": ts, "asset_id": asset_id, "sensor": s, "value": v})
          for s, v in series.items()
      ]
      df = pd.concat(frames, ignore_index=True)
      return Dataset("synthetic_subsea", True, df), truth


if __name__ == "__main__":
      ds, truth = build()
      ds.validate()
      Path("data").mkdir(exist_ok=True)
      ds.readings.to_csv("data/synthetic_readings.csv", index=False)
      Path("data/anomalies_truth.json").write_text(json.dumps(truth, indent=2))
      print(f"Wrote {len(ds.readings)} rows and {len(truth)} truth anomalies")