import pandas as pd

from adapters.synthetic_subsea import build
from core.detector import detect_all
from core.evidence import build_evidence
from core.explain import build_prompt


def _events():
    ds, _ = build()
    return ds.readings, detect_all(ds.readings)


def test_evidence_for_every_event_has_core_fields():
    df, events = _events()
    for e in events:
        ev = build_evidence(df, e)
        assert ev["event_id"] == e["id"]
        assert ev["sensor"] == e["sensor"]
        assert ev["points_in_event"] > 0


def test_missing_data_event_reports_missing_points():
    df, events = _events()
    e = next(x for x in events if x["rule"] == "missing")
    ev = build_evidence(df, e)
    assert ev["missing_points"] == 12
    assert ev["event_min"] is None  # no real values inside a dropout


def test_spike_peak_is_far_above_baseline():
    df, events = _events()
    e = next(x for x in events if x["sensor"] == "pressure" and x["rule"] == "zscore")
    ev = build_evidence(df, e)
    assert ev["peak_deviation_from_baseline"] > 10


def test_prompt_contains_the_evidence_numbers():
    df, events = _events()
    ev = build_evidence(df, events[0])
    prompt = build_prompt(ev)
    assert str(ev["event_max"]) in prompt
    assert "ONLY the numbers" in prompt