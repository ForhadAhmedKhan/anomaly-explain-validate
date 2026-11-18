import numpy as np
import pandas as pd


def _r(x, nd=2):
    return None if x is None or pd.isna(x) else round(float(x), nd)


def build_evidence(readings, event, baseline_points=144):
    """Collect plain facts about one detected event, straight from the data.

    The LLM may only talk about numbers that appear here, and the Week 3
    accuracy checks compare its explanation against this same dictionary.
    """
    g = readings[
        (readings["asset_id"] == event["asset_id"]) & (readings["sensor"] == event["sensor"])
    ].sort_values("timestamp")

    in_event = g[(g["timestamp"] >= event["start"]) & (g["timestamp"] <= event["end"])]
    before = g[g["timestamp"] < event["start"]].tail(baseline_points)["value"].dropna()

    values = in_event["value"].dropna()
    base_mean = before.mean() if len(before) else None
    base_std = before.std() if len(before) > 1 else None

    peak_dev = None
    if base_mean is not None and len(values):
        peak_dev = float(np.max(np.abs(values - base_mean)))

    return {
        "event_id": event["id"],
        "asset_id": event["asset_id"],
        "sensor": event["sensor"],
        "rule": event["rule"],
        "start": str(event["start"]),
        "end": str(event["end"]),
        "points_in_event": int(len(in_event)),
        "duration_minutes": int((event["end"] - event["start"]).total_seconds() // 60) + 10,
        "missing_points": int(in_event["value"].isna().sum()),
        "event_min": _r(values.min()) if len(values) else None,
        "event_max": _r(values.max()) if len(values) else None,
        "baseline_mean": _r(base_mean),
        "baseline_std": _r(base_std),
        "peak_deviation_from_baseline": _r(peak_dev),
    }