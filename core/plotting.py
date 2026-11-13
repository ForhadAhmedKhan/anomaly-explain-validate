from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # draw to files, no window needed
import matplotlib.pyplot as plt
import pandas as pd

PAD = pd.Timedelta(hours=4)  # makes very short events visible on a 30-day chart


def plot_readings(readings, events, truth=None, path="docs/anomaly_chart.png"):
      """One panel per sensor. Red = detected events, green bar = injected truth."""
      sensors = sorted(readings["sensor"].unique())
      fig, axes = plt.subplots(len(sensors), 1, figsize=(12, 3 * len(sensors)), sharex=True)
      if len(sensors) == 1:
          axes = [axes]

      for ax, sensor in zip(axes, sensors):
          g = readings[readings["sensor"] == sensor].sort_values("timestamp")
          ax.plot(g["timestamp"], g["value"], linewidth=0.8, color="#1f77b4")
          ax.set_ylabel(sensor)

          for e in events:
              if e["sensor"] == sensor:
                  ax.axvspan(e["start"] - PAD, e["end"] + PAD, color="red", alpha=0.3)
                  ax.annotate(e["id"], (e["start"], g["value"].max()),
                              fontsize=7, color="red", va="top")

          if truth:
              ymin = ax.get_ylim()[0]
              for t in truth:
                  if t["sensor"] == sensor:
                      ax.hlines(ymin, pd.Timestamp(t["start"]) - PAD,
                                pd.Timestamp(t["end"]) + PAD,
                                color="green", linewidth=6)

      axes[0].set_title("Sensor readings: red = detected, green bar = injected (truth)")
      fig.tight_layout()
      Path(path).parent.mkdir(parents=True, exist_ok=True)
      fig.savefig(path, dpi=120)
      plt.close(fig)
      return path