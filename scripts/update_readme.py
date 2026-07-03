#!/usr/bin/env python3
"""Refreshes README.md, the per-team charts, and the history snapshot.

Designed to be run frequently (every ~15 min) by a GitHub Action. By
default it only does the expensive work (fetch qualifiers/group/knockout,
refit ratings, run 50000 Monte Carlo trajectories, rewrite README) when a
tracked knockout match is about to kick off or has just finished; every
other tick it exits immediately. Pass --force to always refresh (used for
the workflow_dispatch / manual-trigger path).
"""
from __future__ import annotations

import argparse
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from fifa_sim.bracket import build_bracket  # noqa: E402
from fifa_sim.espn_client import fetch_knockout_events  # noqa: E402
from fifa_sim.history import append_snapshot, team_series  # noqa: E402
from fifa_sim.pipeline import build_snapshot  # noqa: E402
from fifa_sim.plotting import (  # noqa: E402
    plot_champion_lollipop,
    plot_team_history,
    plot_top10_champion_timeseries,
)
from fifa_sim.report import (  # noqa: E402
    LOLLIPOP_RELPATH,
    TOP10_TIMESERIES_RELPATH,
    TRACKED_TEAMS,
    render_results_markdown,
    slug_for_team,
    top_champion_teams,
    update_readme,
)
from fifa_sim.scheduler import compute_should_run, load_state, save_state  # noqa: E402
from fifa_sim.simulator import run_simulation  # noqa: E402

README_PATH = os.path.join(REPO_ROOT, "README.md")
PLOTS_DIR = os.path.join(REPO_ROOT, "data", "plots")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="refresh even without a trigger condition")
    parser.add_argument("--n", type=int, default=50000, help="Monte Carlo trajectories (default 50000)")
    args = parser.parse_args(argv)

    bracket = build_bracket(fetch_knockout_events())
    prev_state = load_state()
    decision = compute_should_run(bracket, prev_state)

    if not decision.should_run and not args.force:
        print("No tracked match starting soon or just finished -- skipping refresh.")
        return 0

    if args.force:
        print("Forced refresh.")
    for reason in decision.reasons:
        print(f"Trigger: {reason}")

    snapshot = build_snapshot()
    result = run_simulation(snapshot.bracket, snapshot.ratings, n_trajectories=args.n)
    append_snapshot(result)

    markdown = render_results_markdown(snapshot, result)
    update_readme(README_PATH, markdown)

    os.makedirs(PLOTS_DIR, exist_ok=True)
    for team_name in TRACKED_TEAMS:
        series = team_series(team_name)
        if not series:
            continue
        out_path = os.path.join(PLOTS_DIR, f"{slug_for_team(team_name)}.png")
        plot_team_history(team_name, series, out_path)

    ranked_probs = top_champion_teams(result)
    ranked_series = [(name, team_series(name)) for name, _ in ranked_probs]
    ranked_series = [(name, s) for name, s in ranked_series if s]
    if ranked_series:
        plot_top10_champion_timeseries(
            ranked_series, os.path.join(REPO_ROOT, TOP10_TIMESERIES_RELPATH)
        )

    plot_champion_lollipop(ranked_probs, os.path.join(REPO_ROOT, LOLLIPOP_RELPATH))

    save_state(decision.new_state)
    print(f"Refreshed README with {result.n_trajectories} trajectories.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
