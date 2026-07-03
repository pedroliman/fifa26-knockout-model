"""Wires together: fetch live data -> fit ratings -> build bracket.

This is the single function the CLI calls to go from "nothing" to a fully
resolved, simulation-ready snapshot of the tournament as it stands right
now. Call it again at any point (a minute later, after a goal, the next
day) and every piece re-fetches fresh data.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

from .bracket import Bracket, build_bracket
from .espn_client import (
    fetch_group_stage_events,
    fetch_knockout_events,
    fetch_qualifier_events,
)
from .ratings import MatchResult, TeamRatings, fit_ratings


@dataclass
class Snapshot:
    bracket: Bracket
    ratings: TeamRatings
    n_group_matches: int
    n_knockout_matches_used: int
    n_qualifier_matches: int


def _completed_result(event, neutral: bool) -> MatchResult | None:
    if event.status_state != "post":
        return None
    if event.home.is_placeholder or event.away.is_placeholder:
        return None
    if event.home.score is None or event.away.score is None:
        return None
    return MatchResult(
        home_id=event.home.team_id,
        away_id=event.away.team_id,
        home_name=event.home.name,
        away_name=event.away.name,
        home_goals=event.home.score,
        away_goals=event.away.score,
        date=event.date,
        neutral=neutral,
    )


def build_snapshot() -> Snapshot:
    with ThreadPoolExecutor(max_workers=3) as pool:
        group_future = pool.submit(fetch_group_stage_events)
        knockout_future = pool.submit(fetch_knockout_events)
        qualifier_future = pool.submit(fetch_qualifier_events)
        group_events = group_future.result()
        knockout_events = knockout_future.result()
        qualifier_events = qualifier_future.result()

    results: list[MatchResult] = []

    # Qualifiers are genuine home/away fixtures; every 2026 World Cup match
    # is a neutral venue (except for the hosts, handled by host_boost).
    n_qualifier = 0
    for e in qualifier_events:
        r = _completed_result(e, neutral=False)
        if r is not None:
            results.append(r)
            n_qualifier += 1

    n_group = 0
    for e in group_events:
        r = _completed_result(e, neutral=True)
        if r is not None:
            results.append(r)
            n_group += 1

    n_knockout_used = 0
    for e in knockout_events:
        r = _completed_result(e, neutral=True)
        if r is not None:
            results.append(r)
            n_knockout_used += 1

    ratings = fit_ratings(results)
    bracket = build_bracket(knockout_events)

    return Snapshot(
        bracket=bracket,
        ratings=ratings,
        n_group_matches=n_group,
        n_knockout_matches_used=n_knockout_used,
        n_qualifier_matches=n_qualifier,
    )
