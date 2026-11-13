import json

import pandas as pd

from core.detector import detect_all
from core.plotting import plot_readings

df = pd.read_csv("data/synthetic_readings.csv", parse_dates=["timestamp"])
truth = json.load(open("data/anomalies_truth.json"))
events = detect_all(df)
path = plot_readings(df, events, truth)
print(f"Saved chart to {path}")