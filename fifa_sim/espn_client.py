"""Thin client around ESPN's public (unauthenticated) soccer JSON API.

ESPN does not officially document this API, but it is the same endpoint
that powers espn.com/soccer and requires no API key. We use it for three
things:

1. Live/near-live scoreboard data (score, clock, period) for in-progress
   matches -> lets the model react the instant a goal is scored.
2. Historical match results (group stage + completed knockout matches) ->
   used to fit each team's attack/defense strength.
3. The knockout bracket skeleton itself: ESPN pre-creates a fixture for
   every bracket slot (Round of 32 through the Final) before the teams
   occupying later slots are known, labeling the unresolved side
   "Round of 32 11 Winner" etc. We parse that text to build the bracket
   graph -- no hardcoded matchups anywhere in this codebase.
"""
from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Optional

BASE = "https://site.api.espn.com/apis/site/v2/sports/soccer/fifa.world"
USER_AGENT = "Mozilla/5.0 (compatible; fifa26-knockout-model/0.1; +research use)"

# FIFA World Cup 2026 calendar (fixed, published tournament schedule).
GROUP_STAGE_RANGE = "20260611-20260628"
KNOCKOUT_RANGE = "20260628-20260721"

HOST_NATIONS = {"United States", "Mexico", "Canada"}

ROUND_ORDER = [
    "round-of-32",
    "round-of-16",
    "quarterfinals",
    "semifinals",
    "3rd-place-match",
    "final",
]


def _get(url: str, timeout: float = 15.0, retries: int = 3) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    last_err = None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
            last_err = e
            if attempt < retries - 1:
                time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"Failed to fetch {url}: {last_err}")


def get_scoreboard(date_range: str) -> dict:
    return _get(f"{BASE}/scoreboard?dates={date_range}")


def get_all_teams() -> dict:
    return _get(f"{BASE}/teams?limit=100")


@dataclass
class Competitor:
    team_id: str
    name: str
    is_placeholder: bool
    score: Optional[int]
    winner: Optional[bool]


@dataclass
class RawEvent:
    event_id: int
    date: str
    round_slug: str
    status_state: str  # 'pre' | 'in' | 'post'
    status_description: str
    clock_seconds: float
    period: int
    home: Competitor
    away: Competitor


def _parse_competitor(c: dict) -> Competitor:
    team = c.get("team", {})
    name = team.get("displayName", "?")
    # ESPN pre-creates a placeholder pseudo-team for unresolved bracket slots
    # (e.g. "Round of 32 11 Winner") with a real-looking numeric id but
    # isActive=False -- that's the reliable signal, not id-presence.
    is_placeholder = not team.get("isActive", True)
    score = c.get("score")
    try:
        score = int(score) if score is not None else None
    except (ValueError, TypeError):
        score = None
    return Competitor(
        team_id=str(team.get("id")) if not is_placeholder else "",
        name=name,
        is_placeholder=is_placeholder,
        score=score,
        winner=c.get("winner"),
    )


def parse_events(raw: dict) -> list[RawEvent]:
    events = []
    for e in raw.get("events", []):
        comp = e["competitions"][0]
        status = comp["status"]
        competitors = comp["competitors"]
        home_raw = next(c for c in competitors if c["homeAway"] == "home")
        away_raw = next(c for c in competitors if c["homeAway"] == "away")
        events.append(
            RawEvent(
                event_id=int(e["id"]),
                date=e["date"],
                round_slug=e["season"]["slug"],
                status_state=status["type"]["state"],
                status_description=status["type"]["description"],
                clock_seconds=float(status.get("clock") or 0.0),
                period=int(status.get("period") or 0),
                home=_parse_competitor(home_raw),
                away=_parse_competitor(away_raw),
            )
        )
    return events


def fetch_group_stage_events() -> list[RawEvent]:
    raw = get_scoreboard(GROUP_STAGE_RANGE)
    events = parse_events(raw)
    return [e for e in events if e.round_slug == "group-stage"]


def fetch_knockout_events() -> list[RawEvent]:
    raw = get_scoreboard(KNOCKOUT_RANGE)
    events = parse_events(raw)
    return [e for e in events if e.round_slug in ROUND_ORDER]
