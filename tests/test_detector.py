from adapters.synthetic_subsea import build
from core.detector import detect_zscore
from core.evaluate import score


def test_detector_finds_all_spikes():
      ds, truth = build()
      result = score(detect_zscore(ds.readings), truth)
      found_types = [t["type"] for t in result["found"]]
      assert found_types.count("spike") == 4


def test_events_have_required_fields():
      ds, _ = build()
      events = detect_zscore(ds.readings)
      assert events
      for e in events:
          assert {"id", "asset_id", "sensor", "start", "end", "peak_z"} <= set(e)
          


def test_combined_detector_finds_all_but_drifts():
      from core.detector import detect_all

      ds, truth = build()
      result = score(detect_all(ds.readings), truth)
      missed_types = sorted(t["type"] for t in result["missed"])
      assert missed_types == ["drift", "drift"]
      assert len(result["found"]) == 7


def test_event_ids_are_unique():
      from core.detector import detect_all

      ds, _ = build()
      ids = [e["id"] for e in detect_all(ds.readings)]
      assert len(ids) == len(set(ids))