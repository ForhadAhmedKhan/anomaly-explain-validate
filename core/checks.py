import re

TIMESTAMP = re.compile(r"\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}(?::\d{2})?")
EVENT_ID = re.compile(r"\bD\d{3}\b")
NUMBER = re.compile(r"\d+(?:\.\d+)?")


def numbers_in(text, asset_id=""):
    """Pull the numbers out of an explanation, ignoring timestamps, event IDs and the asset ID."""
    cleaned = TIMESTAMP.sub(" ", text)
    cleaned = EVENT_ID.sub(" ", cleaned)
    if asset_id:
        cleaned = cleaned.replace(asset_id, " ")
    return [float(x) for x in NUMBER.findall(cleaned)]


def allowed_numbers(evidence):
    """Every real number in the evidence (not strings, not None)."""
    return [
        float(v) for v in evidence.values()
        if isinstance(v, (int, float)) and not isinstance(v, bool)
    ]


def check_no_hallucinated_numbers(explanation, evidence, tol=0.005):
    """Return the list of numbers in the explanation that are NOT in the evidence."""
    allowed = allowed_numbers(evidence)
    bad = []
    for n in numbers_in(explanation, evidence.get("asset_id", "")):
        if not any(abs(n - a) <= tol for a in allowed):
            bad.append(n)
    return bad




# ---------------------------------------------------------------------------
#Each returns a list of problems (empty list = pass).
# ---------------------------------------------------------------------------

UP_WORDS = re.compile(
    r"\b(above|higher|rise|rose|risen|elevat\w*|increas\w*|surge\w*|spike\w*|exceed\w*)\b", re.I)
DOWN_WORDS = re.compile(
    r"\b(below|lower|drop|dropped|dropping|fell|fall|decreas\w*|declin\w*|dip\w*|reduc\w*)\b", re.I)

TYPE_WORDS = {
    "flatline": re.compile(r"\b(flatline\w*|flat|constant|frozen|stuck|unchanged|fixed)\b", re.I),
    "missing": re.compile(r"\b(missing|gap|no data|dropout|absent)\b", re.I),
}

NULL_ACK = re.compile(
    r"\b(null|not available|unavailable|no data|no valid|no recorded|insufficient|unknown|"
    r"cannot|could not)\b", re.I)

CAUSE_WORDS = re.compile(r"\b(cause|caused|due to|attributed|result of)\b", re.I)
HEDGE_WORDS = re.compile(r"\b(possible|possibly|could|may|might|potential|potentially)\b", re.I)
CERTAINTY_WORDS = re.compile(r"\b(definitely|certainly|undoubtedly|conclusively|proves?)\b", re.I)


def check_direction(explanation, evidence):
    """For z-score events: 'above' vs 'below' wording must match the data."""
    lo, hi, base = evidence["event_min"], evidence["event_max"], evidence["baseline_mean"]
    if evidence["rule"] != "zscore" or lo is None or hi is None or base is None:
        return []
    if lo > base:   # whole event sits above normal
        wrong = DOWN_WORDS.findall(explanation)
        return [f"data is above baseline but text says: {sorted(set(w.lower() for w in wrong))}"] if wrong else []
    if hi < base:   # whole event sits below normal
        wrong = UP_WORDS.findall(explanation)
        return [f"data is below baseline but text says: {sorted(set(w.lower() for w in wrong))}"] if wrong else []
    return []


def check_event_type_wording(explanation, evidence):
    """The explanation must describe the right kind of anomaly."""
    rule = evidence["rule"]
    if rule in TYPE_WORDS:
        if not TYPE_WORDS[rule].search(explanation):
            return [f"a '{rule}' event is never described as one"]
    elif rule == "zscore":
        if not (UP_WORDS.search(explanation) or DOWN_WORDS.search(explanation)):
            return ["no wording about the reading going above or below normal"]
    return []


def check_null_honesty(explanation, evidence):
    """If the evidence has gaps (null values), the explanation must say so."""
    has_null = any(v is None for k, v in evidence.items()
                   if k in ("event_min", "event_max", "baseline_mean",
                            "baseline_std", "peak_deviation_from_baseline"))
    if has_null and not NULL_ACK.search(explanation):
        return ["evidence has null values but the text does not admit it"]
    return []


def check_hedged_causes(explanation, evidence):
    """Any sentence that names a cause must hedge it. No certainty words anywhere."""
    problems = []
    for sentence in re.split(r"(?<=[.!?])\s+", explanation):
        if CAUSE_WORDS.search(sentence) and not HEDGE_WORDS.search(sentence):
            problems.append(f"unhedged cause: {sentence[:60]}...")
    for w in CERTAINTY_WORDS.findall(explanation):
        problems.append(f"certainty word: {w}")
    return problems


ALL_CHECKS = {
    "numbers": check_no_hallucinated_numbers,
    "direction": check_direction,
    "type_wording": check_event_type_wording,
    "null_honesty": check_null_honesty,
    "hedged_cause": check_hedged_causes,
}