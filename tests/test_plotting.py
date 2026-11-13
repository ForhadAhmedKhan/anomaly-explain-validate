from adapters.synthetic_subsea import build
from core.detector import detect_all
from core.plotting import plot_readings


def test_chart_file_is_created(tmp_path):
      ds, truth = build()
      out = tmp_path / "chart.png"
      plot_readings(ds.readings, detect_all(ds.readings), truth, path=str(out))
      assert out.exists() and out.stat().st_size > 10_000