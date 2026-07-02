# FIFA 2026 Knockout-Phase Monte Carlo Model

A self-contained model of the FIFA World Cup 2026 knockout stage (Round of 32
through the Final). Every run fetches live data, refits team strength, and
simulates the rest of the tournament 1000 times.

```
python -m fifa_sim team Brazil
python -m fifa_sim team Brazil --plot
python -m fifa_sim simulate
python -m fifa_sim bracket
```

## What it does

1. **Pulls live data from ESPN's public soccer API** (no key required):
   group-stage results, every completed/live/upcoming knockout fixture, and
   the current score + game clock for matches in progress.
2. **Reconstructs the bracket graph from the data itself** — not
   hardcoded. ESPN pre-creates a fixture for every bracket slot before the
   occupants are known (e.g. a Round-of-16 game shows `"Round of 32 11
   Winner"` as a placeholder participant until that Round-of-32 match
   finishes). We sort each round's fixtures by event id to recover the
   official slot numbers, parse those placeholder strings, and wire each
   match to the two matches that feed it. This means the bracket always
   reflects whatever FIFA/ESPN currently has scheduled, including if a game
   goes to a replay slot or kickoff times shift.
3. **Fits a Poisson attack/defense rating per team** (`fifa_sim/ratings.py`)
   from every group-stage and completed-knockout match played so far —
   a ridge-regularized Maher/Dixon-Coles-style model:
   `lambda_home = exp(mu + attack_home - defense_away + host_boost)`.
   Ridge shrinkage matters a lot early in the tournament, when most teams
   have only 3-6 games of data — without it, a single 5-0 win would make a
   team look unrealistically dominant.
4. **Simulates each remaining match** with Poisson-distributed goals for
   normal time, then extra time (same per-minute intensity) if still level,
   then a 50/50 penalty shootout if still level after that — matching actual
   knockout-match rules (no away goals, no replays).
5. **Respects live match state**: if a match is in progress, the model
   keeps the actual current score fixed and only simulates the *remaining*
   clock time (using the live period/clock from ESPN), so a goal scored
   right now immediately shifts every downstream probability the next time
   you run the CLI.
6. **Runs 1000 Monte Carlo trajectories** through the whole bracket,
   propagating simulated winners (and, for semifinals, losers, for the
   3rd-place match) round by round, and tallies:
   - P(team reaches Round of 16 / QF / SF / Final)
   - P(team wins the Cup)
7. **Snapshots every run** to `data/history/snapshots.jsonl` (timestamped),
   so `--plot` can chart a team's probabilities evolving over time as new
   results come in. Re-run the CLI whenever you want an updated read (after
   a goal, at halftime, the next matchday, etc.) — every run re-fetches
   fresh data and re-fits the model, nothing is cached.

## Design choices & assumptions (read before trusting the numbers)

- **No pre-tournament priors.** Ratings are fit purely from 2026 World Cup
  matches (group stage + knockout so far) via ridge-shrunk MLE — deliberately
  self-contained (one data source, ESPN, for both fixtures and history) rather
  than depending on an external, hard-to-verify Elo/ranking feed. Early in the
  bracket this means ratings are noisier than a model blended with
  preseason strength would be.
- **Host advantage**: a single shared boost term for the USA/Mexico/Canada
  (this tournament's three co-hosts) is fit from the data rather than
  assumed.
- **Extra time** is modeled at the same goals-per-minute rate as normal
  time (a simplifying assumption; some research suggests fatigue lowers
  scoring rates in ET, but the effect is small and contested).
- **Penalty shootouts are a coin flip.** Deliberately not a function of
  team strength — shootout outcomes are well-documented in the literature
  as close to unpredictable from run-of-play ability.
- **Stoppage time is ignored** in the live-match clock model (matches are
  treated as ending at exactly 90/120 minutes); the effect on remaining-time
  estimates is minor.
- 1000 trajectories gives Monte Carlo error of roughly ±1.5 percentage
  points (at p≈0.5) on any given probability — plenty for these purposes,
  and cheap to bump via `--n`.

## Project layout

```
fifa_sim/
  espn_client.py   HTTP layer + raw event parsing (ESPN's public JSON API)
  bracket.py       Builds the bracket graph from event data (slot numbers,
                   placeholder parsing, feeder wiring)
  ratings.py       Poisson attack/defense model fit (scipy L-BFGS-B)
  match_engine.py  Single-match simulation: normal time -> ET -> penalties,
                   including "resume from a live score + clock" mode
  simulator.py     Monte Carlo loop over the whole bracket
  pipeline.py      Glues fetch -> fit -> bracket into one `build_snapshot()`
  history.py       Append/read timestamped snapshots (for the time-series plot)
  plotting.py      matplotlib probability-over-time chart
  cli.py           `team` / `simulate` / `bracket` subcommands
data/
  history/snapshots.jsonl   append-only run history
  plots/                    generated charts
```

## Requirements

```
pip install -r requirements.txt   # numpy, scipy, matplotlib
```

No API key needed — the ESPN scoreboard endpoint used here
(`site.api.espn.com/apis/site/v2/sports/soccer/fifa.world/...`) is public.
