"""Shared helpers for describing one team's bracket position and outlook.

Used by both the interactive CLI (`cli.py`, plain text) and the GitHub
Action README generator (`scripts/update_readme.py`, Markdown) so the two
don't drift out of sync on what "most likely outcome" or "current status"
means.
"""
from __future__ import annotations

from .bracket import Bracket
from .simulator import PROGRESS_ROUNDS, SimulationResult

ROUND_LABELS = {
    "round-of-32": "Round of 32",
    "round-of-16": "Round of 16",
    "quarterfinals": "Quarterfinals",
    "semifinals": "Semifinals",
    "final": "Final",
}


def find_team(name: str, team_names: dict[str, str]) -> str | None:
    name_lower = name.strip().lower()
    for tid, tname in team_names.items():
        if tname.lower() == name_lower:
            return tid
    matches = [tid for tid, tname in team_names.items() if name_lower in tname.lower()]
    if len(matches) == 1:
        return matches[0]
    return None


def current_match_for_team(bracket: Bracket, team_id: str):
    for m in bracket.all_matches():
        for side, other in ((m.home, m.away), (m.away, m.home)):
            if side.team_id == team_id:
                return m, side, other
    return None, None, None


def describe_status(m, side, other) -> str:
    if m is None:
        return "Not part of the Round of 32 (eliminated in the group stage, or data unavailable)."
    label = ROUND_LABELS.get(m.round_slug, m.round_slug)
    opp = other.team_name or "TBD"
    if m.status_state == "post":
        result = "won" if side.winner else "lost"
        return f"{label}: {result} {side.score}-{other.score} vs {opp}."
    if m.status_state == "in":
        return (
            f"{label}: LIVE now vs {opp} — score {side.score}-{other.score}, "
            f"{m.status_description}."
        )
    return f"{label}: upcoming vs {opp} ({m.date})."


def exit_distribution(result: SimulationResult, team_id: str) -> dict[str, float]:
    """P(team's tournament ends at each stage), summing to 1."""
    reach = {r: result.prob_reach(team_id, r) for r in PROGRESS_ROUNDS}
    champion = result.prob_champion(team_id)
    return {
        "Round of 32": 1 - reach["round-of-16"],
        "Round of 16": reach["round-of-16"] - reach["quarterfinals"],
        "Quarterfinals": reach["quarterfinals"] - reach["semifinals"],
        "Semifinals": reach["semifinals"] - reach["final"],
        "Final (runner-up)": reach["final"] - champion,
        "Champion": champion,
    }
