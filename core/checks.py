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