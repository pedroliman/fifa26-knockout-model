"""Decides whether it's worth doing a full refresh right now.

The GitHub Action runs on a tight cron (every 15 minutes) so it can catch
kickoffs and final whistles promptly, but a full refresh (qualifiers +
group + knockout fetch, 50000-trajectory simulation, README/plot rewrite,
commit) is comparatively expensive and would be noisy if it fired every
tick. Instead we keep a small state file recording each bracket match's
last-seen status, and only do the full refresh when something that
qualifies as "before" or "after" a scheduled game has actually happened
since the last refresh:

  * BEFORE: a match is still scheduled ('pre') but kicks off within the
    next `LOOKAHEAD_MINUTES`.
  * AFTER: a match has transitioned to 'post' (finished) since the state
    file was last written.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone

from .bracket import Bracket

LOOKAHEAD_MINUTES = 20

DEFAULT_STATE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data",
    "state",
    "match_status.json",
)


@dataclass
class ShouldRunResult:
    should_run: bool
    reasons: list[str]
    new_state: dict[str, str]


def load_state(path: str = DEFAULT_STATE_PATH) -> dict[str, str]:
    if not os.path.exists(path):
        return {}
    with open(path) as f:
        return json.load(f)


def save_state(state: dict[str, str], path: str = DEFAULT_STATE_PATH) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(state, f, indent=2, sort_keys=True)
        f.write("\n")


def compute_should_run(
    bracket: Bracket,
    prev_state: dict[str, str],
    now: datetime | None = None,
    lookahead_minutes: float = LOOKAHEAD_MINUTES,
) -> ShouldRunResult:
    now = now or datetime.now(timezone.utc)
    reasons: list[str] = []
    new_state: dict[str, str] = {}
    should_run = False

    for m in bracket.all_matches():
        key = str(m.event_id)
        new_state[key] = m.status_state
        prev = prev_state.get(key)
        matchup = f"{m.home.team_name or 'TBD'} vs {m.away.team_name or 'TBD'}"

        if m.status_state == "post" and prev != "post":
            should_run = True
            reasons.append(f"finished: {matchup}")
        elif m.status_state == "pre":
            kickoff = datetime.fromisoformat(m.date)
            minutes_to_kickoff = (kickoff - now).total_seconds() / 60.0
            if 0 <= minutes_to_kickoff <= lookahead_minutes:
                should_run = True
                reasons.append(f"kicks off in {minutes_to_kickoff:.0f} min: {matchup}")

    return ShouldRunResult(should_run=should_run, reasons=reasons, new_state=new_state)
