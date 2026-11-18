import json
from pathlib import Path

from core.checks import ALL_CHECKS

saved = json.loads(Path("data/explanations.json").read_text())
names = list(ALL_CHECKS)

print("event  " + "  ".join(f"{n:<12}" for n in names))
passed = total = 0
for r in sorted(saved, key=lambda x: x["event_id"]):
    cells = []
    for n in names:
        problems = ALL_CHECKS[n](r["explanation"], r["evidence"])
        total += 1
        passed += not problems
        cells.append(f"{'PASS' if not problems else 'FAIL':<12}")
        if problems:
            print(f"   {r['event_id']} {n}: {problems}")
    print(f"{r['event_id']}   " + "  ".join(cells))

print(f"\nPass rate: {passed}/{total} = {passed / total:.0%}")