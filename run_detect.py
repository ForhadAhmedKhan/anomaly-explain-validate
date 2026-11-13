import json
import pandas as pd
from core.detector import detect_zscore
from core.evaluate import score

df = pd.read_csv("data/synthetic_readings.csv", parse_dates=["timestamp"])
truth = json.load(open("data/anomalies_truth.json"))
events = detect_zscore(df)
r = score(events, truth)
print(f"Detected events: {len(events)}")
print(f"Found {len(r['found'])}/{len(truth)} injected anomalies")
for t in r["missed"]:
      print(f"  MISSED {t['id']} {t['sensor']} {t['type']}")
print(f"False alarms: {len(r['false_alarms'])}")
for e in r["false_alarms"]:
      print(f"  FALSE {e['id']} {e['sensor']} {e['start']}")