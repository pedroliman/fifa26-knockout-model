"""Simulates a single knockout match: normal time -> extra time -> penalties.

Handles three situations identically well:
  * a match that hasn't kicked off yet (full 90 simulated from scratch)
  * a match in progress right now (the *already known* score is kept fixed
    and only the remaining minutes are simulated -- this is what makes the
    model react instantly to a live goal and respect time-left-on-the-clock)
  * a completed match (no simulation at all -- the real outcome is used)
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

REGULATION_MINUTES = 90.0
EXTRA_TIME_MINUTES = 30.0
# Extra time is modeled at the same per-minute scoring intensity as normal
# time. Penalty shootouts are treated as a coin flip: shootout outcomes are
# well documented in the literature to be close to unpredictable from team
# strength, so we don't lean on the (noisy, small-sample) attack/defense
# ratings for them.
PENALTY_HOME_WIN_PROB = 0.5


@dataclass
class MatchOutcome:
    home_goals: int
    away_goals: int
    winner: str  # 'home' or 'away'
    decided_by: str  # 'regulation' | 'extra_time' | 'penalties' | 'actual'


def simulate_from_state(
    rng: np.random.Generator,
    lam_home_90: float,
    lam_away_90: float,
    cur_home: int,
    cur_away: int,
    remaining_regulation_min: float,
    remaining_et_min: float,
) -> MatchOutcome:
    h, a = cur_home, cur_away
    if remaining_regulation_min > 0:
        h += rng.poisson(lam_home_90 / REGULATION_MINUTES * remaining_regulation_min)
        a += rng.poisson(lam_away_90 / REGULATION_MINUTES * remaining_regulation_min)
    if h != a:
        return MatchOutcome(h, a, "home" if h > a else "away", "regulation")

    if remaining_et_min > 0:
        h += rng.poisson(lam_home_90 / REGULATION_MINUTES * remaining_et_min)
        a += rng.poisson(lam_away_90 / REGULATION_MINUTES * remaining_et_min)
    if h != a:
        return MatchOutcome(h, a, "home" if h > a else "away", "extra_time")

    winner = "home" if rng.random() < PENALTY_HOME_WIN_PROB else "away"
    return MatchOutcome(h, a, winner, "penalties")


def simulate_not_started(
    rng: np.random.Generator, lam_home_90: float, lam_away_90: float
) -> MatchOutcome:
    return simulate_from_state(
        rng, lam_home_90, lam_away_90, 0, 0, REGULATION_MINUTES, EXTRA_TIME_MINUTES
    )


def remaining_time_budget(period: int, clock_seconds: float) -> tuple[float, float]:
    """Returns (remaining_regulation_min, remaining_et_min) given the live
    clock. `period` >= 3 means the match is already in extra time."""
    elapsed_min = clock_seconds / 60.0
    if period >= 3:
        total = REGULATION_MINUTES + EXTRA_TIME_MINUTES
        remaining_et = max(0.0, total - elapsed_min)
        return 0.0, remaining_et
    remaining_reg = max(0.0, REGULATION_MINUTES - elapsed_min)
    return remaining_reg, EXTRA_TIME_MINUTES
