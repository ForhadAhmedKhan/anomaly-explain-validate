import json
from pathlib import Path

import pytest

from core.checks import (
    check_direction,
    check_event_type_wording,
    check_hedged_causes,
    check_null_honesty,
)

SAVED = json.loads(Path("data/explanations.json").read_text())
IDS = [r["event_id"] for r in SAVED]


def _get(event_id):
    return next(r for r in SAVED if r["event_id"] == event_id)


# --- real explanations must pass every check --------------------------------

@pytest.mark.parametrize("item", SAVED, ids=IDS)
def test_direction_matches_data(item):
    assert check_direction(item["explanation"], item["evidence"]) == []


@pytest.mark.parametrize("item", SAVED, ids=IDS)
def test_event_type_is_described_correctly(item):
    assert check_event_type_wording(item["explanation"], item["evidence"]) == []


@pytest.mark.parametrize("item", SAVED, ids=IDS)
def test_nulls_are_admitted(item):
    assert check_null_honesty(item["explanation"], item["evidence"]) == []


@pytest.mark.parametrize("item", SAVED, ids=IDS)
def test_causes_are_hedged(item):
    assert check_hedged_causes(item["explanation"], item["evidence"]) == []


# --- checker self-tests: corrupt a real explanation, the checker MUST object -

def test_direction_catches_flipped_word():
    r = _get("D001")  # data is above baseline
    corrupted = r["explanation"].replace("above", "below")
    assert check_direction(corrupted, r["evidence"]) != []


def test_direction_catches_wrong_word_on_a_drop():
    r = _get("D006")  # data is below baseline
    corrupted = r["explanation"].replace("dropped", "rose")
    assert check_direction(corrupted, r["evidence"]) != []


def test_type_wording_catches_flatline_described_vaguely():
    r = _get("D004")
    corrupted = "The vibration sensor on asset SUBSEA-01 showed an anomaly lasting 500 minutes."
    assert check_event_type_wording(corrupted, r["evidence"]) != []


def test_type_wording_catches_missing_event_described_vaguely():
    r = _get("D008")
    corrupted = "The pressure sensor on asset SUBSEA-01 had an anomaly lasting 120 minutes."
    assert check_event_type_wording(corrupted, r["evidence"]) != []


def test_null_honesty_catches_silence_about_nulls():
    r = _get("D008")
    corrupted = "The pressure sensor on asset SUBSEA-01 had 12 missing points over 120 minutes."
    assert check_null_honesty(corrupted, r["evidence"]) != []


def test_hedge_catches_stated_cause():
    r = _get("D001")
    corrupted = "A vibration anomaly was flagged. The cause is mechanical bearing wear."
    assert check_hedged_causes(corrupted, r["evidence"]) != []


def test_hedge_catches_certainty_word():
    r = _get("D001")
    corrupted = r["explanation"] + " This definitely needs repair."
    assert check_hedged_causes(corrupted, r["evidence"]) != []