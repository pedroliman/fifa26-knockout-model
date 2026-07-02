"""Plots a team's advancement probabilities over time (one point added per
CLI run). Uses an ordinal light->dark ramp since the five series (reach
Round of 16 ... win the Cup) are a nested, ordered progression rather than
unrelated categories.
"""
from __future__ import annotations

from datetime import datetime, timedelta

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

SURFACE = "#fcfcfb"
INK_PRIMARY = "#0b0b0b"
INK_SECONDARY = "#52514e"
INK_MUTED = "#898781"
GRIDLINE = "#e1e0d9"
BASELINE = "#c3c2b7"

# Ordinal ramp (light -> dark), one step per bracket stage.
STAGE_SERIES = [
    ("reach_round-of-16", "Reach Round of 16", "#86b6ef"),
    ("reach_quarterfinals", "Reach Quarterfinals", "#5598e7"),
    ("reach_semifinals", "Reach Semifinals", "#2a78d6"),
    ("reach_final", "Reach Final", "#1c5cab"),
    ("champion", "Win the Cup", "#104281"),
]


def plot_team_history(team_name: str, series: list[dict], out_path: str) -> str:
    fig, ax = plt.subplots(figsize=(8, 5), facecolor=SURFACE)
    ax.set_facecolor(SURFACE)

    times = [datetime.fromisoformat(s["timestamp"]) for s in series]

    for key, label, color in STAGE_SERIES:
        ys = [s.get(key, 0.0) * 100 for s in series]
        ax.plot(
            times,
            ys,
            label=label,
            color=color,
            linewidth=2,
            marker="o",
            markersize=6,
            markeredgewidth=0,
            solid_capstyle="round",
        )

    ax.set_ylim(0, 100)
    ax.set_ylabel("Probability (%)", color=INK_SECONDARY)
    ax.set_title(f"{team_name} — knockout-stage probability over time", color=INK_PRIMARY, fontsize=13, loc="left")

    ax.grid(axis="y", color=GRIDLINE, linewidth=1)
    ax.grid(axis="x", visible=False)
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color(BASELINE)
    ax.tick_params(colors=INK_MUTED, length=0)

    if len(times) == 1:
        ax.set_xlim(times[0] - timedelta(hours=12), times[0] + timedelta(hours=12))
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=6))
        ax.text(
            0.5,
            -0.22,
            "Only one snapshot so far — re-run the CLI later (e.g. after each match) to build a trend line.",
            transform=ax.transAxes,
            ha="center",
            fontsize=8,
            color=INK_MUTED,
        )
    else:
        ax.xaxis.set_major_locator(mdates.AutoDateLocator(maxticks=8))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d %H:%M"))
    fig.autofmt_xdate(rotation=30, ha="right")

    legend = ax.legend(
        loc="upper left",
        bbox_to_anchor=(1.02, 1.0),
        frameon=False,
        labelcolor=INK_SECONDARY,
        fontsize=9,
    )

    fig.tight_layout()
    fig.savefig(out_path, dpi=150, facecolor=SURFACE, bbox_inches="tight")
    plt.close(fig)
    return out_path
