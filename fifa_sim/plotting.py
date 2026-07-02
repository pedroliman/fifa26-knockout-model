"""Plots for the knockout model:

- `plot_team_history`: one team's advancement probabilities over time.
- `plot_top10_champion_timeseries` / `plot_champion_lollipop`: the two
  social-media-ready charts embedded at the top of the README, both
  flag-illustrated and set in large type for legibility at feed size.
"""
from __future__ import annotations

from datetime import datetime, timedelta

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from matplotlib.offsetbox import AnnotationBbox, OffsetImage

from .flags import flag_path

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

# Categorical palette (fixed order), extended to 10 slots. Identity in the
# social charts is carried primarily by the flag + direct label at each
# mark, so the two extra slots reusing a step is a minor, acceptable
# tradeoff rather than a reason to introduce a second, less legible hue.
CATEGORICAL_10 = [
    "#2a78d6",  # blue
    "#1baf7a",  # aqua
    "#eda100",  # yellow
    "#008300",  # green
    "#4a3aa7",  # violet
    "#e34948",  # red
    "#e87ba4",  # magenta
    "#eb6834",  # orange
    "#256abf",  # blue, deeper step
    "#0d366b",  # blue, deepest step
]


def _add_flag(ax, x: float, y: float, team_name: str, zoom: float, xycoords="data", box_alignment=(0.5, 0.5)):
    """Places a small flag thumbnail at (x, y); no-ops if unavailable."""
    path = flag_path(team_name)
    if path is None:
        return
    try:
        img = mpimg.imread(path)
    except (OSError, ValueError):
        return
    imagebox = OffsetImage(img, zoom=zoom)
    imagebox.image.axes = ax
    ab = AnnotationBbox(
        imagebox,
        (x, y),
        xycoords=xycoords,
        frameon=True,
        pad=0.15,
        bboxprops=dict(edgecolor=BASELINE, linewidth=1.0),
        box_alignment=box_alignment,
        zorder=5,
    )
    ax.add_artist(ab)


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


def plot_top10_champion_timeseries(ranked_series: list[tuple[str, list[dict]]], out_path: str) -> str:
    """`ranked_series` is [(team_name, series), ...] for the top 10 teams by
    *current* title probability, each series a list of
    {"timestamp": iso8601, "champion": 0..1, ...} dicts from history.py,
    already ordered best-to-worst. Big type, flag + direct label at the end
    of each line -- designed to be screenshotted straight into a social post.
    """
    with plt.rc_context({"font.family": "sans-serif"}):
        n = len(ranked_series)
        fig, ax = plt.subplots(figsize=(14, max(8, 0.85 * n + 2)), facecolor=SURFACE)
        ax.set_facecolor(SURFACE)

        all_times: list[datetime] = []
        endpoints: list[tuple[str, datetime, float, str]] = []  # name, x, y, color
        for i, (team_name, series) in enumerate(ranked_series):
            if not series:
                continue
            times = [datetime.fromisoformat(s["timestamp"]) for s in series]
            ys = [s.get("champion", 0.0) * 100 for s in series]
            all_times.extend(times)
            color = CATEGORICAL_10[i % len(CATEGORICAL_10)]
            ax.plot(
                times, ys, color=color, linewidth=3.5, marker="o", markersize=9,
                markeredgewidth=0, solid_capstyle="round", zorder=3,
            )
            endpoints.append((team_name, times[-1], ys[-1], color))

        tmin, tmax = min(all_times), max(all_times)
        if tmin == tmax:
            tmin, tmax = tmin - timedelta(hours=12), tmax + timedelta(hours=12)
        span = tmax - tmin
        rail_x = tmax + span * 0.10
        ax.set_xlim(tmin - span * 0.03, tmax + span * 0.62)

        all_ys = [s.get("champion", 0.0) * 100 for _, series in ranked_series for s in series]
        y_lo, y_hi = min(all_ys), max(all_ys)
        pad = max((y_hi - y_lo) * 0.12, 1.0)
        ax.set_ylim(max(0, y_lo - pad), y_hi + pad)
        axis_lo, axis_hi = ax.get_ylim()

        # Evenly spaced label rail (best team at top), so labels never
        # collide even when several teams' probabilities are close together.
        rail_top = axis_hi - (axis_hi - axis_lo) * 0.04
        rail_bottom = axis_lo + (axis_hi - axis_lo) * 0.04
        rail_ys = (
            [rail_top - i * (rail_top - rail_bottom) / (n - 1) for i in range(n)]
            if n > 1
            else [(rail_top + rail_bottom) / 2]
        )

        for (team_name, ex, ey, color), rail_y in zip(endpoints, rail_ys):
            ax.plot(
                [ex, rail_x], [ey, rail_y], color=color, linewidth=1.25,
                alpha=0.55, zorder=2, clip_on=False,
            )
            _add_flag(ax, rail_x, rail_y, team_name, zoom=0.11, box_alignment=(0.5, 0.5))
            ax.annotate(
                f"{team_name}  {ey:.1f}%",
                (rail_x, rail_y),
                xytext=(30, 0),
                textcoords="offset points",
                va="center",
                fontsize=17,
                fontweight="bold",
                color=INK_PRIMARY,
                clip_on=False,
            )

        ax.set_ylabel("Win-the-Cup probability (%)", fontsize=20, color=INK_SECONDARY, labelpad=12)
        ax.set_title(
            "FIFA World Cup 2026 — Top 10 title-probability trend",
            fontsize=27, color=INK_PRIMARY, loc="left", fontweight="bold", pad=18,
        )

        ax.grid(axis="y", color=GRIDLINE, linewidth=1)
        ax.grid(axis="x", visible=False)
        for spine in ("top", "right", "left"):
            ax.spines[spine].set_visible(False)
        ax.spines["bottom"].set_color(BASELINE)
        ax.tick_params(colors=INK_MUTED, length=0, labelsize=16)
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d\n%H:%M"))

        fig.tight_layout()
        fig.savefig(out_path, dpi=200, facecolor=SURFACE, bbox_inches="tight")
        plt.close(fig)
    return out_path


def plot_champion_lollipop(ranked_probs: list[tuple[str, float]], out_path: str) -> str:
    """`ranked_probs` is [(team_name, champion_probability_0_to_1), ...],
    already sorted best-to-worst. One lollipop per team: a stem from 0 to
    the probability, the team's flag at the tip, and a bold direct label.
    """
    n = len(ranked_probs)
    fig, ax = plt.subplots(figsize=(12, 0.95 * n + 1.5), facecolor=SURFACE)
    ax.set_facecolor(SURFACE)

    max_pct = max(p for _, p in ranked_probs) * 100 if ranked_probs else 1.0
    ys = list(range(n, 0, -1))
    for i, (y, (team_name, prob)) in enumerate(zip(ys, ranked_probs)):
        pct = prob * 100
        color = CATEGORICAL_10[i % len(CATEGORICAL_10)]
        ax.plot([0, pct], [y, y], color=color, linewidth=4, solid_capstyle="round", zorder=1, alpha=0.85)
        _add_flag(ax, pct, y, team_name, zoom=0.17)
        ax.annotate(
            f"{team_name} — {pct:.1f}%",
            (pct, y),
            xytext=(40, 0),
            textcoords="offset points",
            va="center",
            fontsize=18,
            fontweight="bold",
            color=INK_PRIMARY,
            clip_on=False,
        )

    ax.set_yticks([])
    ax.set_xlim(0, max_pct * 1.9 + 5)
    ax.set_ylim(0.3, n + 0.7)
    ax.set_xlabel("Win-the-Cup probability (%)", fontsize=20, color=INK_SECONDARY, labelpad=12)
    ax.set_title(
        "FIFA World Cup 2026 — Title-probability leaderboard",
        fontsize=27, color=INK_PRIMARY, loc="left", fontweight="bold", pad=18,
    )

    ax.grid(axis="x", color=GRIDLINE, linewidth=1)
    ax.grid(axis="y", visible=False)
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color(BASELINE)
    ax.tick_params(colors=INK_MUTED, length=0, labelsize=16)

    fig.tight_layout()
    fig.savefig(out_path, dpi=200, facecolor=SURFACE, bbox_inches="tight")
    plt.close(fig)
    return out_path
