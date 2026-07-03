"""Monte Carlo engine: simulates the whole knockout bracket N times.

Each trajectory walks the bracket round by round (Round of 32 -> Final).
For every match:
  * if it's already finished, the real result is used (no randomness)
  * if it's live right now, the real *current* score is kept and only the
    clock's remaining minutes are simulated
  * if it hasn't started, the full match is simulated from 0-0

Winners (and, for semifinals, losers -- needed for the 3rd place match)
propagate forward into whichever later match ESPN says depends on them,
so the bracket resolves itself trajectory by trajectory.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field

import numpy as np

from .bracket import Bracket, KnockoutMatch, Side
from .espn_client import ROUND_ORDER
from .match_engine import (
    advance_probability,
    remaining_time_budget,
    simulate_from_state,
)
from .ratings import TeamRatings

PROGRESS_ROUNDS = ["round-of-32", "round-of-16", "quarterfinals", "semifinals", "final"]


@dataclass
class SimulationResult:
    n_trajectories: int
    team_names: dict[str, str]
    reach_counts: dict[str, dict[str, int]]  # team_id -> round_slug -> count
    champion_counts: dict[str, int]
    third_place_counts: dict[str, int]

    def prob_reach(self, team_id: str, round_slug: str) -> float:
        return self.reach_counts.get(team_id, {}).get(round_slug, 0) / self.n_trajectories

    def prob_champion(self, team_id: str) -> float:
        return self.champion_counts.get(team_id, 0) / self.n_trajectories

    def prob_third_place(self, team_id: str) -> float:
        return self.third_place_counts.get(team_id, 0) / self.n_trajectories

    def all_r32_teams(self) -> list[str]:
        return list(self.reach_counts.keys())


def _resolve_side(
    side: Side,
    resolved_winner: dict[tuple[str, int], str],
    resolved_loser: dict[tuple[str, int], str],
) -> str:
    if side.team_id:
        return side.team_id
    assert side.feeder is not None, f"Unresolved side with no feeder: {side}"
    key = (side.feeder.round_slug, side.feeder.slot)
    if side.feeder.outcome == "Winner":
        return resolved_winner[key]
    return resolved_loser[key]


def _resolve_match(
    m: KnockoutMatch,
    home_id: str,
    away_id: str,
    ratings: TeamRatings,
    rng: np.random.Generator,
    advance_cache: dict[tuple[str, str], float],
) -> tuple[str, str]:
    """Returns (winner_id, loser_id) for this match, simulating live/future
    matches and reusing the real outcome for completed ones."""
    if m.status_state == "post":
        if m.home.winner:
            return home_id, away_id
        if m.away.winner:
            return away_id, home_id
        # Defensive fallback (should not happen for a decided knockout match).
        return (home_id, away_id) if (m.home.score or 0) >= (m.away.score or 0) else (
            away_id,
            home_id,
        )

    if m.status_state == "in":
        lam_home = ratings.lam(home_id, away_id)
        lam_away = ratings.lam(away_id, home_id)
        remaining_reg, remaining_et = remaining_time_budget(m.period, m.clock_seconds)
        outcome = simulate_from_state(
            rng,
            lam_home,
            lam_away,
            m.home.score or 0,
            m.away.score or 0,
            remaining_reg,
            remaining_et,
        )
        if outcome.winner == "home":
            return home_id, away_id
        return away_id, home_id

    # 'pre': the exact advance probability for this pairing only depends on
    # the two teams, so compute it once (analytically, from the Poisson score
    # grid) and resolve every trajectory with a single Bernoulli draw. Same
    # distribution as simulating the goals, but with the per-match sampling
    # noise removed -- which is what makes 50k+ trajectories cheap.
    key = (home_id, away_id)
    p_home = advance_cache.get(key)
    if p_home is None:
        p_home = advance_probability(
            ratings.lam(home_id, away_id), ratings.lam(away_id, home_id)
        )
        advance_cache[key] = p_home
    if rng.random() < p_home:
        return home_id, away_id
    return away_id, home_id


def run_simulation(
    bracket: Bracket,
    ratings: TeamRatings,
    n_trajectories: int = 10000,
    seed: int | None = None,
) -> SimulationResult:
    rng = np.random.default_rng(seed)
    advance_cache: dict[tuple[str, str], float] = {}

    r32_teams = bracket.round_of_32_teams()
    reach_counts: dict[str, dict[str, int]] = {t: defaultdict(int) for t in r32_teams}
    champion_counts: dict[str, int] = defaultdict(int)
    third_place_counts: dict[str, int] = defaultdict(int)

    for _ in range(n_trajectories):
        resolved_winner: dict[tuple[str, int], str] = {}
        resolved_loser: dict[tuple[str, int], str] = {}

        for slug in ROUND_ORDER:
            for m in bracket.matches_by_round.get(slug, []):
                home_id = _resolve_side(m.home, resolved_winner, resolved_loser)
                away_id = _resolve_side(m.away, resolved_winner, resolved_loser)

                if slug in PROGRESS_ROUNDS:
                    reach_counts[home_id][slug] += 1
                    reach_counts[away_id][slug] += 1

                winner_id, loser_id = _resolve_match(
                    m, home_id, away_id, ratings, rng, advance_cache
                )
                resolved_winner[(slug, m.slot)] = winner_id
                resolved_loser[(slug, m.slot)] = loser_id

                if slug == "final":
                    champion_counts[winner_id] += 1
                if slug == "3rd-place-match":
                    third_place_counts[winner_id] += 1

    return SimulationResult(
        n_trajectories=n_trajectories,
        team_names=dict(ratings.team_names),
        reach_counts={t: dict(v) for t, v in reach_counts.items()},
        champion_counts=dict(champion_counts),
        third_place_counts=dict(third_place_counts),
    )
