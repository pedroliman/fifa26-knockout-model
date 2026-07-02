# FIFA 2026 Knockout-Phase Monte Carlo Model

<!-- RESULTS:START -->
_Last updated: 2026-07-02 21:31 UTC — 1000 simulated trajectories, fit on 911 qualifiers + 72 group + 11 completed knockout matches._

## Current standings

| Team | R16 | QF | SF | Final | Champion |
|---|---:|---:|---:|---:|---:|
| Spain | 100.0% | 68.8% | 44.5% | 26.8% | **15.8%** |
| France | 100.0% | 76.0% | 49.0% | 27.2% | **15.0%** |
| Mexico | 100.0% | 52.5% | 33.2% | 21.1% | **11.8%** |
| England | 100.0% | 47.5% | 28.0% | 17.7% | **10.3%** |
| Norway | 100.0% | 59.8% | 24.7% | 14.4% | **7.0%** |
| Belgium | 100.0% | 53.0% | 23.1% | 11.4% | **5.9%** |
| Argentina | 68.7% | 39.6% | 23.7% | 12.3% | **5.2%** |
| Canada | 100.0% | 48.1% | 18.7% | 8.6% | **4.5%** |
| Morocco | 100.0% | 51.9% | 23.8% | 8.6% | **4.0%** |
| Switzerland | 68.9% | 35.7% | 19.0% | 8.5% | **3.8%** |
| United States | 100.0% | 47.0% | 17.8% | 8.2% | **3.6%** |
| Brazil | 100.0% | 40.2% | 14.1% | 7.1% | **3.3%** |
| Portugal | 57.0% | 19.3% | 9.5% | 4.5% | **2.1%** |
| Egypt | 49.1% | 28.1% | 14.7% | 5.3% | **1.8%** |
| Ghana | 55.1% | 25.9% | 12.6% | 4.1% | **1.5%** |
| Australia | 50.9% | 27.4% | 12.4% | 4.3% | **1.3%** |
| Colombia | 44.9% | 18.6% | 7.9% | 2.6% | **1.0%** |
| Croatia | 43.0% | 11.9% | 5.1% | 2.4% | **0.9%** |
| Paraguay | 100.0% | 24.0% | 8.5% | 2.3% | **0.6%** |
| Algeria | 31.1% | 10.7% | 4.1% | 1.3% | **0.3%** |
| Cape Verde | 31.3% | 14.0% | 5.6% | 1.3% | **0.3%** |
| Ecuador | 0.0% | 0.0% | 0.0% | 0.0% | **0.0%** |
| Germany | 0.0% | 0.0% | 0.0% | 0.0% | **0.0%** |
| Senegal | 0.0% | 0.0% | 0.0% | 0.0% | **0.0%** |
| Netherlands | 0.0% | 0.0% | 0.0% | 0.0% | **0.0%** |
| Japan | 0.0% | 0.0% | 0.0% | 0.0% | **0.0%** |
| Sweden | 0.0% | 0.0% | 0.0% | 0.0% | **0.0%** |
| Congo DR | 0.0% | 0.0% | 0.0% | 0.0% | **0.0%** |
| Austria | 0.0% | 0.0% | 0.0% | 0.0% | **0.0%** |
| Ivory Coast | 0.0% | 0.0% | 0.0% | 0.0% | **0.0%** |
| Bosnia-Herzegovina | 0.0% | 0.0% | 0.0% | 0.0% | **0.0%** |
| South Africa | 0.0% | 0.0% | 0.0% | 0.0% | **0.0%** |

## Team spotlight

### Brazil

Round of 32: won 2-1 vs Japan.

| Stage | P(reach) |
|---|---:|
| Round of 16 | 100.0% |
| Quarterfinals | 40.2% |
| Semifinals | 14.1% |
| Final | 7.1% |
| **Win the Cup** | **3.3%** |

Most likely single outcome: **Round of 16** (59.8%).

![Brazil probability over time](data/plots/brazil.png)

### France

Round of 32: won 3-0 vs Sweden.

| Stage | P(reach) |
|---|---:|
| Round of 16 | 100.0% |
| Quarterfinals | 76.0% |
| Semifinals | 49.0% |
| Final | 27.2% |
| **Win the Cup** | **15.0%** |

Most likely single outcome: **Quarterfinals** (27.0%).

![France probability over time](data/plots/france.png)

### United States

Round of 32: won 2-0 vs Bosnia-Herzegovina.

| Stage | P(reach) |
|---|---:|
| Round of 16 | 100.0% |
| Quarterfinals | 47.0% |
| Semifinals | 17.8% |
| Final | 8.2% |
| **Win the Cup** | **3.6%** |

Most likely single outcome: **Round of 16** (53.0%).

![United States probability over time](data/plots/united_states.png)

### Argentina

Round of 32: upcoming vs Cape Verde (2026-07-03T22:00Z).

| Stage | P(reach) |
|---|---:|
| Round of 16 | 68.7% |
| Quarterfinals | 39.6% |
| Semifinals | 23.7% |
| Final | 12.3% |
| **Win the Cup** | **5.2%** |

Most likely single outcome: **Round of 32** (31.3%).

![Argentina probability over time](data/plots/argentina.png)

### Spain

Round of 32: won 3-0 vs Austria.

| Stage | P(reach) |
|---|---:|
| Round of 16 | 100.0% |
| Quarterfinals | 68.8% |
| Semifinals | 44.5% |
| Final | 26.8% |
| **Win the Cup** | **15.8%** |

Most likely single outcome: **Round of 16** (31.2%).

![Spain probability over time](data/plots/spain.png)

<!-- RESULTS:END -->

A self-contained model of the FIFA World Cup 2026 knockout stage (Round of 32
through the Final). Every run fetches live data, refits team strength, and
simulates the rest of the tournament 1000 times.

The **Current standings** and **Team spotlight** sections above are
regenerated automatically by a GitHub Action — see
[Automation](#automation) below. Everything below this point is static
documentation of how the model works.

```
python -m fifa_sim team Brazil
python -m fifa_sim team Brazil --plot
python -m fifa_sim simulate
python -m fifa_sim bracket
```

## What it does

1. **Pulls live data from ESPN's public soccer API** (no key required):
   2026 World Cup qualifying results for all six confederations (UEFA,
   CONMEBOL, CONCACAF, CAF, AFC, OFC), group-stage results, every
   completed/live/upcoming knockout fixture, and the current score + game
   clock for matches in progress. ESPN uses one global team-id namespace
   across all of these competitions, so a qualifier result for team "164"
   (Spain) joins directly onto its World Cup rows -- no name-matching
   needed.
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
   from every qualifying, group-stage, and completed-knockout match played
   so far — a ridge-regularized Maher/Dixon-Coles-style model:
   `lambda_home = exp(mu + attack_home - defense_away + host_boost)`.
   Every match is exponentially down-weighted by how long ago it was played
   (365-day half-life), so a 2023 qualifier barely counts, a late-2025
   qualifier counts for a good deal, and this tournament's own matches count
   almost fully — one continuous discount instead of a separate, harder-to-
   justify "qualifiers are worth X%" knob. Ridge shrinkage on top of that
   still matters early in the tournament, when a team might have only 3-6
   *World Cup* games — without it, a single 5-0 win would make a team look
   unrealistically dominant.
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

- **No external Elo/ranking prior.** Ratings are fit purely from ESPN match
  data (qualifiers + 2026 World Cup) via recency-weighted, ridge-shrunk MLE —
  deliberately self-contained (one data source for both fixtures and
  history) rather than depending on a separate, hard-to-verify ranking feed.
  Qualifiers substantially reduce (but don't eliminate) the small-sample
  noise for teams early in the World Cup bracket.
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

## Automation

`.github/workflows/update-knockout-stats.yml` runs `scripts/update_readme.py`
on a 15-minute cron (plus manual `workflow_dispatch`) for the duration of the
knockout stage (2026-06-27 through 2026-07-20; the workflow no-ops outside
that window to avoid burning Actions minutes for the rest of the year).

Most ticks are a no-op. `fifa_sim/scheduler.py` keeps a small state file
(`data/state/match_status.json`) of each bracket match's last-seen status
and only triggers the expensive path — refetch qualifiers/group/knockout,
refit ratings, run 1000 trajectories, rewrite the README, regenerate charts,
commit, push — when:

- a match is scheduled to kick off within the next 20 minutes (**before**), or
- a match has transitioned to finished since the last update (**after**).

So every scheduled game gets a stats refresh shortly before kickoff and
again the moment it ends, plus README updates for both. A manual run via
`workflow_dispatch` (with `force: true`) always refreshes regardless.

The **Team spotlight** section tracks five teams: Brazil, France, the
United States, Argentina, and Spain (`fifa_sim/report.py::TRACKED_TEAMS`) —
edit that list to track different teams. The general leaderboard covers all
32 Round-of-32 teams regardless.

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
  team_status.py   Shared "find team / current match / exit distribution"
                   helpers used by both the CLI and the README report
  report.py        Renders the Markdown block injected into README.md
  scheduler.py      Decides whether a refresh is due right now (see Automation)
  cli.py           `team` / `simulate` / `bracket` subcommands
scripts/
  update_readme.py  Entry point the GitHub Action runs
data/
  history/snapshots.jsonl   append-only run history
  plots/                    generated charts (including the 5 tracked teams)
  state/match_status.json   last-seen status per bracket match
.github/workflows/
  update-knockout-stats.yml   the scheduled/on-demand automation
```

## Requirements

```
pip install -r requirements.txt   # numpy, scipy, matplotlib
```

No API key needed — the ESPN scoreboard endpoint used here
(`site.api.espn.com/apis/site/v2/sports/soccer/fifa.world/...`) is public.