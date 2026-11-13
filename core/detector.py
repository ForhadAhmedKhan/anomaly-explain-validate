import pandas as pd


def detect_zscore(readings, window=144, threshold=4.0, max_gap=3):
      """Flag points far from the rolling mean, then merge nearby flags into events."""
      events = []
      for (asset_id, sensor), g in readings.groupby(["asset_id", "sensor"]):
          g = g.sort_values("timestamp").reset_index(drop=True)
          roll = g["value"].rolling(window, min_periods=window // 2)
          z = (g["value"] - roll.mean()) / roll.std()
          flagged = g.index[z.abs() > threshold].tolist()
          if not flagged:
              continue
          start = prev = flagged[0]
          groups = []
          for i in flagged[1:]:
              if i - prev > max_gap:
                  groups.append((start, prev))
                  start = i
              prev = i
          groups.append((start, prev))
          for s, e in groups:
              events.append({
                  "asset_id": asset_id,
                  "sensor": sensor,
                  "start": g.loc[s, "timestamp"],
                  "end": g.loc[e, "timestamp"],
                  "peak_z": round(float(z.iloc[s:e + 1].abs().max()), 2),
              })
      events.sort(key=lambda e: e["start"])
      for n, e in enumerate(events, start=1):
          e["id"] = f"D{n:03d}"
      return events