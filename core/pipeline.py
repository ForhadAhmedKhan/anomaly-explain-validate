import json
import time
from pathlib import Path

from core.evidence import build_evidence


def _load(path):
    p = Path(path)
    return json.loads(p.read_text()) if p.exists() else []


def explain_all(readings, events, explain_fn, model_name="",
                path="data/explanations.json", delay=4.0, attempts=3):
    """Explain every event and save results. Re-running skips finished events.

    An old explanation is reused only if its evidence is identical, so changing
    the detector can never leave a stale explanation behind.
    """
    saved = {r["event_id"]: r for r in _load(path)}
    failed = []

    for event in events:
        evidence = build_evidence(readings, event)
        old = saved.get(event["id"])
        if old and old["evidence"] == evidence:
            continue  # already explained, evidence unchanged

        text = None
        for attempt in range(1, attempts + 1):
            try:
                text = explain_fn(evidence)
                break
            except Exception as err:  # network, quota, bad model name...
                print(f"  {event['id']} attempt {attempt} failed: {err}")
                time.sleep(delay * attempt)
        if text is None:
            failed.append(event["id"])
            continue

        saved[event["id"]] = {
            "event_id": event["id"],
            "evidence": evidence,
            "explanation": text.strip(),
            "model": model_name,
        }
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(json.dumps(list(saved.values()), indent=2))  # save after each one
        time.sleep(delay)  # stay under free-tier rate limits

    results = sorted(saved.values(), key=lambda r: r["event_id"])
    return results, failed