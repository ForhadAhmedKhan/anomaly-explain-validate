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