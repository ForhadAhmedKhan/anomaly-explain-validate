import pandas as pd


def score(events, truth):
      """A truth anomaly is found if any detected event on the same sensor overlaps it."""
      found, missed = [], []
      matched_events = set()
      for t in truth:
          ts, te = pd.Timestamp(t["start"]), pd.Timestamp(t["end"])
          hit = [e for e in events
                 if e["sensor"] == t["sensor"] and e["start"] <= te and e["end"] >= ts]
          if hit:
              found.append(t)
              matched_events.update(e["id"] for e in hit)
          else:
              missed.append(t)
      false_alarms = [e for e in events if e["id"] not in matched_events]
      return {"found": found, "missed": missed, "false_alarms": false_alarms}