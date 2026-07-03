# FIFA 2026 Knockout-Phase Monte Carlo Model

<!-- RESULTS:START -->
_Last updated: **2026-07-03 01:21:44 UTC** by local/manual run — 1000 simulated trajectories, fit on 911 qualifiers + 72 group + 12 completed knockout matches._

![Title-probability trend, top contenders](data/plots/top10_champion_trend.png)

![Title-probability leaderboard](data/plots/champion_lollipop.png)

## Current standings

| Team | R16 | QF | SF | Final | Champion |
|---|---:|---:|---:|---:|---:|
| Spain | 100.0% | 67.5% | 42.6% | 25.4% | **14.9%** |
| France | 100.0% | 74.8% | 47.3% | 24.6% | **14.9%** |
| Mexico | 100.0% | 52.8% | 32.8% | 21.3% | **12.8%** |
| England | 100.0% | 47.2% | 29.3% | 18.2% | **10.0%** |
| Norway | 100.0% | 59.0% | 22.9% | 13.1% | **5.9%** |
| Belgium | 100.0% | 54.9% | 24.5% | 12.4% | **5.8%** |
| Argentina | 66.7% | 39.4% | 22.7% | 10.2% | **4.4%** |
| Switzerland | 70.4% | 38.5% | 21.8% | 9.4% | **4.4%** |
| United States | 100.0% | 45.1% | 18.2% | 9.0% | **4.3%** |
| Canada | 100.0% | 51.2% | 22.2% | 9.3% | **4.1%** |
| Morocco | 100.0% | 48.8% | 21.3% | 9.5% | **4.0%** |
| Brazil | 100.0% | 41.0% | 15.0% | 7.4% | **3.2%** |
| Portugal | 100.0% | 32.5% | 14.7% | 6.6% | **2.4%** |
| Australia | 49.0% | 24.3% | 12.0% | 5.0% | **2.4%** |
| Ghana | 56.8% | 27.0% | 12.7% | 5.1% | **2.1%** |
| Colombia | 43.2% | 21.5% | 9.2% | 3.0% | **1.4%** |
| Egypt | 51.0% | 27.2% | 12.1% | 4.9% | **1.2%** |
| Paraguay | 100.0% | 25.2% | 9.2% | 3.2% | **1.1%** |
| Cape Verde | 33.3% | 12.3% | 5.4% | 1.3% | **0.4%** |
| Algeria | 29.6% | 9.8% | 4.1% | 1.1% | **0.3%** |
| Ivory Coast | 0.0% | 0.0% | 0.0% | 0.0% | **0.0%** |
| Austria | 0.0% | 0.0% | 0.0% | 0.0% | **0.0%** |
| Senegal | 0.0% | 0.0% | 0.0% | 0.0% | **0.0%** |
| Croatia | 0.0% | 0.0% | 0.0% | 0.0% | **0.0%** |
| Japan | 0.0% | 0.0% | 0.0% | 0.0% | **0.0%** |
| Germany | 0.0% | 0.0% | 0.0% | 0.0% | **0.0%** |
| Netherlands | 0.0% | 0.0% | 0.0% | 0.0% | **0.0%** |
| Bosnia-Herzegovina | 0.0% | 0.0% | 0.0% | 0.0% | **0.0%** |
| Congo DR | 0.0% | 0.0% | 0.0% | 0.0% | **0.0%** |
| South Africa | 0.0% | 0.0% | 0.0% | 0.0% | **0.0%** |
| Ecuador | 0.0% | 0.0% | 0.0% | 0.0% | **0.0%** |
| Sweden | 0.0% | 0.0% | 0.0% | 0.0% | **0.0%** |

## Team spotlight

### Brazil

Round of 32: won 2-1 vs Japan.

| Stage | P(reach) |
|---|---:|
| Round of 16 | 100.0% |
| Quarterfinals | 41.0% |
| Semifinals | 15.0% |
| Final | 7.4% |
| **Win the Cup** | **3.2%** |

Most likely single outcome: **Round of 16** (59.0%).

![Brazil probability over time](data/plots/brazil.png)

### France

Round of 32: won 3-0 vs Sweden.

| Stage | P(reach) |
|---|---:|
| Round of 16 | 100.0% |
| Quarterfinals | 74.8% |
| Semifinals | 47.3% |
| Final | 24.6% |
| **Win the Cup** | **14.9%** |

Most likely single outcome: **Quarterfinals** (27.5%).

![France probability over time](data/plots/france.png)

### United States

Round of 32: won 2-0 vs Bosnia-Herzegovina.

| Stage | P(reach) |
|---|---:|
| Round of 16 | 100.0% |
| Quarterfinals | 45.1% |
| Semifinals | 18.2% |
| Final | 9.0% |
| **Win the Cup** | **4.3%** |

Most likely single outcome: **Round of 16** (54.9%).

![United States probability over time](data/plots/united_states.png)

### Argentina

Round of 32: upcoming vs Cape Verde (2026-07-03T22:00Z).

| Stage | P(reach) |
|---|---:|
| Round of 16 | 66.7% |
| Quarterfinals | 39.4% |
| Semifinals | 22.7% |
| Final | 10.2% |
| **Win the Cup** | **4.4%** |

Most likely single outcome: **Round of 32** (33.3%).

![Argentina probability over time](data/plots/argentina.png)

### Spain

Round of 32: won 3-0 vs Austria.

| Stage | P(reach) |
|---|---:|
| Round of 16 | 100.0% |
| Quarterfinals | 67.5% |
| Semifinals | 42.6% |
| Final | 25.4% |
| **Win the Cup** | **14.9%** |

Most likely single outcome: **Round of 16** (32.5%).

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
`workflow_dispatch` always forces a refresh regardless of the trigger
conditions.

Every refresh timestamps the README (`_Last updated: ..._`) and links back
to the GitHub Actions run that produced it (`fifa_sim/report.py::_run_provenance`,
via the `GITHUB_RUN_ID`/`GITHUB_SERVER_URL` env vars GitHub sets automatically)
so you can always tell exactly which run last touched the numbers — it
falls back to "local/manual run" when the script is run outside CI.

Two flag-illustrated, large-type charts (`fifa_sim/plotting.py`,
`fifa_sim/flags.py`) sit at the top of the results, sized to be
screenshotted straight into a social post:

- **Title-probability trend** — a time series of Win-the-Cup probability
  for the current top 10 teams, one line per team, with an evenly spaced
  label rail (flag + name + %) on the right so labels never collide even
  when several teams are bunched together.
- **Title-probability leaderboard** — a lollipop chart of the same set,
  each stem tipped with the team's flag.

Both always include Brazil (`fifa_sim/report.py::ALWAYS_INCLUDE_SOCIAL`),
appended after the top 10 on any run where they don't make it on merit —
edit that tuple to always-include different teams.

Flags are fetched once from flagcdn.com (by ISO 3166-1 code, England/
Scotland/Wales via flagcdn's subdivision codes) and cached under
`data/cache/flags/`.

The **Team spotlight** section tracks five teams: Brazil, France, the
United States, Argentina, and Spain (`fifa_sim/report.py::TRACKED_TEAMS`) —
edit that list to track different teams. The general leaderboard and the
two social charts cover all 32 Round-of-32 teams / the current top 10
regardless.

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
  history.py       Append/read timestamped snapshots (for the time-series plots)
  plotting.py      matplotlib charts: per-team history, top-10 trend, lollipop
  flags.py         Fetches + caches team flag PNGs (flagcdn.com) for the charts
  team_status.py   Shared "find team / current match / exit distribution"
                   helpers used by both the CLI and the README report
  report.py        Renders the Markdown block injected into README.md
  scheduler.py      Decides whether a refresh is due right now (see Automation)
  cli.py           `team` / `simulate` / `bracket` subcommands
scripts/
  update_readme.py  Entry point the GitHub Action runs
data/
  history/snapshots.jsonl   append-only run history
  plots/                    generated charts (5 tracked teams + 2 social charts)
  state/match_status.json   last-seen status per bracket match
  cache/flags/              cached flag PNGs
.github/workflows/
  update-knockout-stats.yml   the scheduled/on-demand automation
```

## Requirements

```
pip install -r requirements.txt   # numpy, scipy, matplotlib
```

No API key needed — the ESPN scoreboard endpoint used here
(`site.api.espn.com/apis/site/v2/sports/soccer/fifa.world/...`) is public.