"""Append-only time series of simulation results, so probabilities can be
plotted over time as the tournament (and the data feeding the model)
progresses. Every `simulate`/`team` CLI run appends one snapshot.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone

from .simulator import PROGRESS_ROUNDS, SimulationResult

DEFAULT_HISTORY_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "history", "snapshots.jsonl"
)


def append_snapshot(result: SimulationResult, path: str = DEFAULT_HISTORY_PATH) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "n_trajectories": result.n_trajectories,
        "teams": {},
    }
    for team_id in result.all_r32_teams():
        record["teams"][team_id] = {
            "name": result.team_names.get(team_id, team_id),
            **{f"reach_{r}": result.prob_reach(team_id, r) for r in PROGRESS_ROUNDS},
            "champion": result.prob_champion(team_id),
            "third_place": result.prob_third_place(team_id),
        }
    with open(path, "a") as f:
        f.write(json.dumps(record) + "\n")


def load_history(path: str = DEFAULT_HISTORY_PATH) -> list[dict]:
    if not os.path.exists(path):
        return []
    snapshots = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                snapshots.append(json.loads(line))
    return snapshots


def team_series(team_name: str, path: str = DEFAULT_HISTORY_PATH) -> list[dict]:
    """Returns [{timestamp, reach_round-of-16, ..., champion}, ...] for the
    named team (case-insensitive match on team name) across all snapshots
    that included it."""
    series = []
    for snap in load_history(path):
        for team_id, data in snap["teams"].items():
            if data["name"].lower() == team_name.lower():
                series.append({"timestamp": snap["timestamp"], **data})
                break
    return series
