import json
from pathlib import Path

import pytest

from core.checks import check_no_hallucinated_numbers, numbers_in

SAVED = json.loads(Path("data/explanations.json").read_text())


# --- the checker itself ---------------------------------------------------

def test_numbers_in_ignores_timestamps_and_asset_id():
    text = "SUBSEA-01 at 2026-01-05 04:00:00 hit 5.24 for 30 minutes."
    assert numbers_in(text, "SUBSEA-01") == [5.24, 30.0]


# --- check 1: every real explanation must be free of invented numbers -----

@pytest.mark.parametrize("item", SAVED, ids=[r["event_id"] for r in SAVED])
def test_no_hallucinated_numbers(item):
    bad = check_no_hallucinated_numbers(item["explanation"], item["evidence"])
    assert bad == [], f"{item['event_id']} contains numbers not in the evidence: {bad}"


# --- checker self-tests: corrupt a real explanation, the checker MUST object

def _d001():
    return next(r for r in SAVED if r["event_id"] == "D001")


def test_checker_catches_a_changed_number():
    r = _d001()
    corrupted = r["explanation"].replace("4.99", "5.99")
    assert check_no_hallucinated_numbers(corrupted, r["evidence"]) == [5.99]


def test_checker_catches_a_changed_duration():
    r = _d001()
    corrupted = r["explanation"].replace("30 minutes", "45 minutes")
    assert 45.0 in check_no_hallucinated_numbers(corrupted, r["evidence"])


def test_checker_catches_an_invented_statistic():
    r = _d001()
    corrupted = r["explanation"] + " There is a 95% chance of failure within 3 days."
    assert 95.0 in check_no_hallucinated_numbers(corrupted, r["evidence"])