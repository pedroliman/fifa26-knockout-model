"""Fits a Maher/Dixon-Coles-style Poisson attack/defense rating for every
team from every 2026 World Cup *qualifying* match plus the 2026 World Cup
matches played so far (group stage + any completed knockout matches). This
is the "estimate a model from up-to-date data" piece: everything here is
derived from ESPN's own match results, re-fit every time the CLI runs, so
ratings drift as new results come in.

Model
-----
For a match between team i and team j:
    lambda_i = exp(mu + attack_i - defense_j + host_boost * hosts(i))
    lambda_j = exp(mu + attack_j - defense_i + host_boost * hosts(j))
goals_i ~ Poisson(lambda_i), goals_j ~ Poisson(lambda_j)

`hosts(t)` is 1 for the three co-host nations (USA/Mexico/Canada), 0
otherwise -- a small shared home-advantage term since every match in this
tournament is played on their soil.

Attack/defense parameters are ridge-shrunk toward 0 (i.e. toward
league-average strength). This matters a lot early in the tournament, when
a team might have only 3-6 World Cup matches of data, so unregularized
per-team MLE would be extremely noisy (a team that wins 5-0 once would
otherwise look like the best attack in the world). Qualifiers add a couple
of years and dozens of extra matches per team, which is exactly the extra
signal that makes the shrinkage bite less.

Every match is also exponentially time-decayed by recency (`_recency_weight`)
relative to today: a qualifier from early 2023 barely moves the needle, a
qualifier from late 2025 counts for a good deal, and this tournament's own
matches (days to weeks old) count almost fully. This lets qualifiers and
World Cup matches share one likelihood without a second, harder-to-justify
"qualifiers are worth X%" knob -- the discount is purely "how long ago",
which also means the model naturally forgets stale qualifier form as the
tournament goes on and its own matches pile up.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

import numpy as np
from scipy.optimize import minimize

from .espn_client import HOST_NATIONS

RIDGE_LAMBDA = 2.0  # shrinkage strength on attack/defense terms
HOST_RIDGE_LAMBDA = 4.0  # extra shrinkage on the single host-advantage term
RECENCY_HALF_LIFE_DAYS = 365.0  # a match this many days old counts for half


@dataclass
class MatchResult:
    home_id: str
    away_id: str
    home_name: str
    away_name: str
    home_goals: int
    away_goals: int
    date: str  # ISO 8601, e.g. "2025-03-21T19:00Z"


def _recency_weight(date_str: str, as_of: datetime) -> float:
    played = datetime.fromisoformat(date_str)
    days_ago = max(0.0, (as_of - played).total_seconds() / 86400.0)
    return 0.5 ** (days_ago / RECENCY_HALF_LIFE_DAYS)


@dataclass
class TeamRatings:
    mu: float
    host_boost: float
    attack: dict[str, float]
    defense: dict[str, float]
    team_names: dict[str, str]

    def lam(self, team_id: str, opponent_id: str) -> float:
        host = 1.0 if self.team_names.get(team_id) in HOST_NATIONS else 0.0
        val = (
            self.mu
            + self.attack.get(team_id, 0.0)
            - self.defense.get(opponent_id, 0.0)
            + self.host_boost * host
        )
        return float(np.exp(val))


def fit_ratings(results: list[MatchResult], as_of: datetime | None = None) -> TeamRatings:
    as_of = as_of or datetime.now(timezone.utc)
    team_ids = sorted({r.home_id for r in results} | {r.away_id for r in results})
    team_names = {}
    for r in results:
        team_names[r.home_id] = r.home_name
        team_names[r.away_id] = r.away_name
    idx = {t: i for i, t in enumerate(team_ids)}
    n = len(team_ids)

    home_idx = np.array([idx[r.home_id] for r in results])
    away_idx = np.array([idx[r.away_id] for r in results])
    home_goals = np.array([r.home_goals for r in results], dtype=float)
    away_goals = np.array([r.away_goals for r in results], dtype=float)
    weights = np.array([_recency_weight(r.date, as_of) for r in results])
    home_is_host = np.array(
        [1.0 if team_names[r.home_id] in HOST_NATIONS else 0.0 for r in results]
    )
    away_is_host = np.array(
        [1.0 if team_names[r.away_id] in HOST_NATIONS else 0.0 for r in results]
    )

    # params = [mu, host_boost, attack(n), defense(n)]
    x0 = np.zeros(2 + 2 * n)

    def unpack(x):
        mu, host_boost = x[0], x[1]
        attack = x[2 : 2 + n]
        defense = x[2 + n : 2 + 2 * n]
        return mu, host_boost, attack, defense

    def neg_log_likelihood(x):
        mu, host_boost, attack, defense = unpack(x)
        lam_home = np.exp(mu + attack[home_idx] - defense[away_idx] + host_boost * home_is_host)
        lam_away = np.exp(mu + attack[away_idx] - defense[home_idx] + host_boost * away_is_host)
        # Poisson NLL up to a goals! constant (doesn't affect the optimum),
        # each observation down-weighted by how long ago it was played.
        nll = np.sum(weights * (lam_home - home_goals * np.log(lam_home)))
        nll += np.sum(weights * (lam_away - away_goals * np.log(lam_away)))
        nll += RIDGE_LAMBDA * (np.sum(attack**2) + np.sum(defense**2))
        nll += HOST_RIDGE_LAMBDA * host_boost**2
        return nll

    res = minimize(neg_log_likelihood, x0, method="L-BFGS-B")
    mu, host_boost, attack, defense = unpack(res.x)

    return TeamRatings(
        mu=float(mu),
        host_boost=float(host_boost),
        attack={t: float(attack[idx[t]]) for t in team_ids},
        defense={t: float(defense[idx[t]]) for t in team_ids},
        team_names=team_names,
    )
