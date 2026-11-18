import json

from adapters.synthetic_subsea import build
from core.detector import detect_all
from core.pipeline import explain_all


def _setup():
    ds, _ = build()
    return ds.readings, detect_all(ds.readings)


def test_explains_every_event_and_saves_file(tmp_path):
    df, events = _setup()
    path = tmp_path / "exp.json"
    results, failed = explain_all(df, events, lambda ev: "fake text", path=str(path), delay=0)
    assert failed == []
    assert len(results) == len(events)
    assert len(json.loads(path.read_text())) == len(events)


def test_second_run_makes_no_new_calls(tmp_path):
    df, events = _setup()
    path = str(tmp_path / "exp.json")
    explain_all(df, events, lambda ev: "fake", path=path, delay=0)
    calls = []
    explain_all(df, events, lambda ev: calls.append(1) or "fake", path=path, delay=0)
    assert calls == []


def test_retries_then_succeeds(tmp_path):
    df, events = _setup()
    state = {"n": 0}

    def flaky(ev):
        state["n"] += 1
        if state["n"] == 1:
            raise RuntimeError("temporary glitch")
        return "ok"

    results, failed = explain_all(df, events[:1], flaky, path=str(tmp_path / "e.json"), delay=0)
    assert failed == [] and len(results) == 1


def test_permanent_failure_is_reported_not_saved(tmp_path):
    df, events = _setup()

    def broken(ev):
        raise RuntimeError("quota")

    path = tmp_path / "e.json"
    results, failed = explain_all(df, events[:1], broken, path=str(path), delay=0)
    assert failed == [events[0]["id"]] and results == []