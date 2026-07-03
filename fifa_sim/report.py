"""Renders the simulation as a Markdown block for the README.

Kept separate from `cli.py` (plain text) but built on the same shared
`team_status` helpers, so the numbers and wording never drift between the
two surfaces.
"""
from __future__ import annotations

import os
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

EASTERN = ZoneInfo("America/New_York")

from .pipeline import Snapshot
from .simulator import PROGRESS_ROUNDS, SimulationResult
from .team_status import (
    ROUND_LABELS,
    current_match_for_team,
    describe_status,
    exit_distribution,
    find_team,
)

RESULTS_START = "<!-- RESULTS:START -->"
RESULTS_END = "<!-- RESULTS:END -->"

TRACKED_TEAMS = ["Brazil", "France", "United States", "Argentina", "Spain"]

TOP_N_SOCIAL = 10
ALWAYS_INCLUDE_SOCIAL = ("Brazil",)
TOP10_TIMESERIES_RELPATH = "data/plots/top10_champion_trend.png"
LOLLIPOP_RELPATH = "data/plots/champion_lollipop.png"


def slug_for_team(team_name: str) -> str:
    return team_name.lower().replace(" ", "_")


def top_champion_teams(
    result: SimulationResult,
    n: int = TOP_N_SOCIAL,
    always_include: tuple[str, ...] = ALWAYS_INCLUDE_SOCIAL,
) -> list[tuple[str, float]]:
    """[(team_name, champion_probability), ...] ranked best-first, for the
    top `n` teams. Any name in `always_include` that didn't make the top n
    on its own merit is appended at the end (it necessarily has a lower
    probability than everyone already in the list, so the result stays in
    descending order) -- e.g. Brazil is always shown on the social charts
    even in a bracket run where they're not a top-10 favorite."""
    ranked = sorted(
        result.all_r32_teams(),
        key=lambda tid: -result.prob_champion(tid),
    )
    ranked_names = [result.team_names.get(tid, tid) for tid in ranked]
    top = ranked_names[:n]
    for name in always_include:
        if name not in top and name in ranked_names:
            top.append(name)

    name_to_id = {result.team_names.get(tid, tid): tid for tid in ranked}
    return [(name, result.prob_champion(name_to_id[name])) for name in top]


def _run_provenance() -> str:
    server = os.environ.get("GITHUB_SERVER_URL")
    repo = os.environ.get("GITHUB_REPOSITORY")
    run_id = os.environ.get("GITHUB_RUN_ID")
    event = os.environ.get("GITHUB_EVENT_NAME")
    if server and repo and run_id:
        url = f"{server}/{repo}/actions/runs/{run_id}"
        suffix = f" ({event})" if event else ""
        return f"[GitHub Actions run #{run_id}]({url}){suffix}"
    return "local/manual run"


def _leaderboard_table(result: SimulationResult) -> str:
    rows = []
    for team_id in result.all_r32_teams():
        rows.append(
            (
                result.team_names.get(team_id, team_id),
                result.prob_reach(team_id, "round-of-16"),
                result.prob_reach(team_id, "quarterfinals"),
                result.prob_reach(team_id, "semifinals"),
                result.prob_reach(team_id, "final"),
                result.prob_champion(team_id),
            )
        )
    rows.sort(key=lambda r: -r[5])

    lines = [
        "| Team | R16 | QF | SF | Final | Champion |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for name, r16, qf, sf, f, champ in rows:
        lines.append(
            f"| {name} | {r16*100:.1f}% | {qf*100:.1f}% | {sf*100:.1f}% | "
            f"{f*100:.1f}% | **{champ*100:.1f}%** |"
        )
    return "\n".join(lines)


def _team_section(snapshot: Snapshot, result: SimulationResult, team_name: str) -> str:
    team_id = find_team(team_name, snapshot.ratings.team_names)
    if team_id is None or team_id not in snapshot.bracket.round_of_32_teams():
        return f"### {team_name}\n\nNot in the Round of 32 (eliminated in the group stage).\n"

    m, side, other = current_match_for_team(snapshot.bracket, team_id)
    status = describe_status(m, side, other)

    reach = {r: result.prob_reach(team_id, r) for r in PROGRESS_ROUNDS}
    champion = result.prob_champion(team_id)
    exits = exit_distribution(result, team_id)
    most_likely = max(exits, key=exits.get)

    lines = [
        f"### {team_name}",
        "",
        status,
        "",
        "| Stage | P(reach) |",
        "|---|---:|",
    ]
    for r in PROGRESS_ROUNDS[1:]:
        lines.append(f"| {ROUND_LABELS[r]} | {reach[r]*100:.1f}% |")
    lines.append(f"| **Win the Cup** | **{champion*100:.1f}%** |")
    lines.append("")
    lines.append(f"Most likely single outcome: **{most_likely}** ({exits[most_likely]*100:.1f}%).")
    lines.append("")
    lines.append(f"![{team_name} probability over time](data/plots/{slug_for_team(team_name)}.png)")
    return "\n".join(lines)


def render_results_markdown(
    snapshot: Snapshot,
    result: SimulationResult,
    tracked_teams: list[str] = TRACKED_TEAMS,
) -> str:
    now = datetime.now(timezone.utc).astimezone(EASTERN).strftime("%Y-%m-%d %H:%M:%S %Z")
    parts = [
        RESULTS_START,
        f"_Last updated: **{now}** by {_run_provenance()} — {result.n_trajectories} simulated "
        f"trajectories, fit on {snapshot.n_qualifier_matches} qualifiers + {snapshot.n_group_matches} "
        f"group + {snapshot.n_knockout_matches_used} completed knockout matches._",
        "",
        f"![Title-probability trend, top contenders]({TOP10_TIMESERIES_RELPATH})",
        "",
        f"![Title-probability leaderboard]({LOLLIPOP_RELPATH})",
        "",
        "## Current standings",
        "",
        _leaderboard_table(result),
        "",
        "## Team spotlight",
        "",
    ]
    for team_name in tracked_teams:
        parts.append(_team_section(snapshot, result, team_name))
        parts.append("")
    parts.append(RESULTS_END)
    return "\n".join(parts)


def update_readme(readme_path: str, results_markdown: str) -> None:
    with open(readme_path) as f:
        content = f.read()

    if RESULTS_START in content and RESULTS_END in content:
        before = content.split(RESULTS_START)[0]
        after = content.split(RESULTS_END)[1]
        new_content = before + results_markdown + after
    else:
        # First run: insert right after the top-level title line.
        lines = content.splitlines()
        insert_at = 1 if lines and lines[0].startswith("# ") else 0
        new_content = "\n".join(
            lines[:insert_at] + ["", results_markdown, ""] + lines[insert_at:]
        )

    with open(readme_path, "w") as f:
        f.write(new_content)
