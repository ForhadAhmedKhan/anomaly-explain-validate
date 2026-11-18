import json

import pandas as pd

from core.detector import detect_all
from core.evidence import build_evidence
from core.explain import explain

df = pd.read_csv("data/synthetic_readings.csv", parse_dates=["timestamp"])
events = detect_all(df)

event = events[0]  # the first detected anomaly
evidence = build_evidence(df, event)
print("EVIDENCE:")
print(json.dumps(evidence, indent=2))
print("\nEXPLANATION:")
print(explain(evidence))