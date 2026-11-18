import os

import pandas as pd
from dotenv import load_dotenv

from core.detector import detect_all
from core.explain import explain
from core.pipeline import explain_all

load_dotenv()
df = pd.read_csv("data/synthetic_readings.csv", parse_dates=["timestamp"])
events = detect_all(df)

results, failed = explain_all(df, events, explain, model_name=os.getenv("GEMINI_MODEL", ""))

for r in results:
    print(f"{r['event_id']} [{r['evidence']['sensor']}/{r['evidence']['rule']}]")
    print("  " + r["explanation"][:160].replace("\n", " "))
print(f"\nExplained {len(results)}/{len(events)} events. Failed: {failed or 'none'}")