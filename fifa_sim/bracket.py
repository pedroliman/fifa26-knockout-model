"""Builds the knockout bracket graph purely from ESPN event data.

Key trick: within each round, ESPN's internal event IDs sort into the same
order as the round's official slot numbers (verified empirically: e.g. the
Round-of-32 event that ESPN privately calls slot 11 is exactly the one
whose id is 11th-smallest among that round's ids, and a still-unresolved
Round-of-16 fixture literally displays "Round of 32 11 Winner" as one of
its two participants). So we never hardcode which countries meet whom --
we sort each round's fixtures by id to recover slot numbers, and parse
placeholder participant text ("Round of 32 11 Winner", "Semifinal 2
Loser", ...) to wire each match to the two matches that feed it.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

from .espn_client import ROUND_ORDER, RawEvent

_PLACEHOLDER_RE = re.compile(
    r"^(Round of \d+|Quarterfinal|Semifinal)\s+(\d+)\s+(Winner|Loser)$"
)

_ROUND_NAME_TO_SLUG = {
    "Round of 32": "round-of-32",
    "Round of 16": "round-of-16",
    "Quarterfinal": "quarterfinals",
    "Semifinal": "semifinals",
}


@dataclass
class Feeder:
    round_slug: str
    slot: int
    outcome: str  # 'Winner' or 'Loser'


@dataclass
class Side:
    team_id: Optional[str]  # None until resolved
    team_name: Optional[str]
    score: Optional[int]
    winner: Optional[bool]
    feeder: Optional[Feeder]  # how to resolve this side if team_id is None


@dataclass
class KnockoutMatch:
    event_id: int
    round_slug: str
    slot: int  # 1-based position within the round
    date: str
    status_state: str
    status_description: str
    clock_seconds: float
    period: int
    home: Side
    away: Side


def _side_from_competitor(c) -> Side:
    if not c.is_placeholder:
        return Side(
            team_id=c.team_id,
            team_name=c.name,
            score=c.score,
            winner=c.winner,
            feeder=None,
        )
    m = _PLACEHOLDER_RE.match(c.name.strip())
    if not m:
        # Unknown placeholder shape; leave fully unresolved with no feeder.
        return Side(
            team_id=None, team_name=c.name, score=c.score, winner=None, feeder=None
        )
    round_name, slot_str, outcome = m.groups()
    slug = _ROUND_NAME_TO_SLUG[round_name]
    return Side(
        team_id=None,
        team_name=c.name,
        score=c.score,
        winner=None,
        feeder=Feeder(round_slug=slug, slot=int(slot_str), outcome=outcome),
    )


class Bracket:
    def __init__(self, matches_by_round: dict[str, list[KnockoutMatch]]):
        self.matches_by_round = matches_by_round
        self._by_slot = {
            (m.round_slug, m.slot): m
            for matches in matches_by_round.values()
            for m in matches
        }

    def get(self, round_slug: str, slot: int) -> KnockoutMatch:
        return self._by_slot[(round_slug, slot)]

    def all_matches(self):
        for slug in ROUND_ORDER:
            for m in self.matches_by_round.get(slug, []):
                yield m

    def round_of_32_teams(self) -> set[str]:
        teams = set()
        for m in self.matches_by_round.get("round-of-32", []):
            if m.home.team_id:
                teams.add(m.home.team_id)
            if m.away.team_id:
                teams.add(m.away.team_id)
        return teams


def build_bracket(events: list[RawEvent]) -> Bracket:
    by_round: dict[str, list[RawEvent]] = {slug: [] for slug in ROUND_ORDER}
    for e in events:
        by_round.setdefault(e.round_slug, []).append(e)

    matches_by_round: dict[str, list[KnockoutMatch]] = {}
    for slug in ROUND_ORDER:
        round_events = sorted(by_round.get(slug, []), key=lambda e: e.event_id)
        matches = []
        for i, e in enumerate(round_events, start=1):
            matches.append(
                KnockoutMatch(
                    event_id=e.event_id,
                    round_slug=slug,
                    slot=i,
                    date=e.date,
                    status_state=e.status_state,
                    status_description=e.status_description,
                    clock_seconds=e.clock_seconds,
                    period=e.period,
                    home=_side_from_competitor(e.home),
                    away=_side_from_competitor(e.away),
                )
            )
        matches_by_round[slug] = matches
    return Bracket(matches_by_round)
