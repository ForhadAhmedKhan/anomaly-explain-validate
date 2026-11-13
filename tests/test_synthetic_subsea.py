import pandas as pd
from adapters.synthetic_subsea import build


def test_is_labeled_synthetic_and_valid():
      ds, truth = build()
      ds.validate()
      assert ds.is_synthetic is True


def test_same_seed_gives_same_data():
      a, _ = build(seed=1)
      b, _ = build(seed=1)
      pd.testing.assert_frame_equal(a.readings, b.readings)


def test_truth_and_dropout_counts():
      ds, truth = build()
      assert len(truth) == 9
      assert ds.readings["value"].isna().sum() == 12