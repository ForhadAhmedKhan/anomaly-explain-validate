import pandas as pd


def _assign_ids(events):
      events.sort(key=lambda e: e["start"])
      for n, e in enumerate(events, start=1):
          e["id"] = f"D{n:03d}"
      return events


def _runs(mask):
      """Yield (start_idx, end_idx) for each run of True values in a boolean Series."""
      run_id = (mask != mask.shift()).cumsum()
      for _, idx in mask.groupby(run_id):
          if idx.iloc[0]:
              yield idx.index[0], idx.index[-1]


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
                  "rule": "zscore",
                  "start": g.loc[s, "timestamp"],
                  "end": g.loc[e, "timestamp"],
                  "peak_z": round(float(z.iloc[s:e + 1].abs().max()), 2),
              })
      return _assign_ids(events)


def detect_missing(readings, min_len=3):
      """Flag runs of missing (NaN) values."""
      events = []
      for (asset_id, sensor), g in readings.groupby(["asset_id", "sensor"]):
          g = g.sort_values("timestamp").reset_index(drop=True)
          for s, e in _runs(g["value"].isna()):
              if e - s + 1 >= min_len:
                  events.append({
                      "asset_id": asset_id,
                      "sensor": sensor,
                      "rule": "missing",
                      "start": g.loc[s, "timestamp"],
                      "end": g.loc[e, "timestamp"],
                      "missing_points": int(e - s + 1),
                  })
      return _assign_ids(events)


def detect_flatline(readings, min_len=10):
      """Flag runs where the exact same value repeats (a frozen sensor)."""
      events = []
      for (asset_id, sensor), g in readings.groupby(["asset_id", "sensor"]):
          g = g.sort_values("timestamp").reset_index(drop=True)
          same = g["value"].eq(g["value"].shift())
          for s, e in _runs(same):
              # a run of repeats starts one point before the first repeat
              s = s - 1
              if e - s + 1 >= min_len:
                  events.append({
                      "asset_id": asset_id,
                      "sensor": sensor,
                      "rule": "flatline",
                      "start": g.loc[s, "timestamp"],
                      "end": g.loc[e, "timestamp"],
                      "frozen_value": round(float(g.loc[s, "value"]), 3),
                  })
      return _assign_ids(events)


def detect_all(readings):
      """Run every rule and return one combined, time-sorted list of events."""
      events = detect_zscore(readings) + detect_missing(readings) + detect_flatline(readings)
      return _assign_ids(events)