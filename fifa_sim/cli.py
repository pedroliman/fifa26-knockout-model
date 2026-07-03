"""Clean CLI for the FIFA 2026 knockout-phase Monte Carlo model.

Examples
--------
    python -m fifa_sim team Brazil
    python -m fifa_sim team Brazil --plot
    python -m fifa_sim simulate
    python -m fifa_sim bracket
"""
from __future__ import annotations

import argparse
import os
import sys
import time

from .history import DEFAULT_HISTORY_PATH, append_snapshot, team_series
from .pipeline import Snapshot, build_snapshot
from .plotting import plot_team_history
from .simulator import PROGRESS_ROUNDS, SimulationResult, run_simulation
from .team_status import (
    ROUND_LABELS,
    current_match_for_team,
    describe_status,
    exit_distribution,
    find_team,
)

PLOTS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "plots"
)


def _print_team_report(snapshot: Snapshot, result: SimulationResult, team_id: str, team_name: str):
    m, side, other = current_match_for_team(snapshot.bracket, team_id)
    print(f"\n=== {team_name} — FIFA World Cup 2026 knockout outlook ===")
    print(describe_status(m, side, other))
    print(f"\nModel: attack={snapshot.ratings.attack.get(team_id, 0.0):+.2f}, "
          f"defense={snapshot.ratings.defense.get(team_id, 0.0):+.2f} "
          f"(fit on {snapshot.n_qualifier_matches} qualifiers + {snapshot.n_group_matches} "
          f"group + {snapshot.n_knockout_matches_used} completed knockout matches, "
          f"recency-weighted)")

    reach = {r: result.prob_reach(team_id, r) for r in PROGRESS_ROUNDS}
    champion = result.prob_champion(team_id)

    print(f"\n{'Stage':<20}{'P(reach)':>12}")
    for r in PROGRESS_ROUNDS[1:]:
        print(f"{ROUND_LABELS[r]:<20}{reach[r]*100:>11.1f}%")
    print(f"{'Win the Cup':<20}{champion*100:>11.1f}%")

    exits = exit_distribution(result, team_id)
    most_likely = max(exits, key=exits.get)
    print(f"\nMost likely single outcome: {most_likely} ({exits[most_likely]*100:.1f}%)")
    print(f"(based on {result.n_trajectories} simulated trajectories)")


def cmd_team(args):
    snapshot = build_snapshot()
    team_id = find_team(args.name, snapshot.ratings.team_names)
    if team_id is None or team_id not in snapshot.bracket.round_of_32_teams():
        available = sorted(
            n for tid, n in snapshot.ratings.team_names.items()
            if tid in snapshot.bracket.round_of_32_teams()
        )
        print(f"'{args.name}' not found among the 32 Round-of-32 teams.", file=sys.stderr)
        print("Available: " + ", ".join(available), file=sys.stderr)
        return 1

    result = run_simulation(snapshot.bracket, snapshot.ratings, n_trajectories=args.n, seed=args.seed)
    team_name = snapshot.ratings.team_names[team_id]
    _print_team_report(snapshot, result, team_id, team_name)

    if not args.no_save:
        append_snapshot(result)

    if args.plot:
        os.makedirs(PLOTS_DIR, exist_ok=True)
        series = team_series(team_name)
        out_path = os.path.join(PLOTS_DIR, f"{team_name.lower().replace(' ', '_')}.png")
        plot_team_history(team_name, series, out_path)
        print(f"\nSaved probability-over-time chart to {out_path}")
    return 0


def cmd_simulate(args):
    snapshot = build_snapshot()
    result = run_simulation(snapshot.bracket, snapshot.ratings, n_trajectories=args.n, seed=args.seed)

    rows = []
    for team_id in result.all_r32_teams():
        rows.append(
            (
                result.team_names.get(team_id, team_id),
                result.prob_reach(team_id, "round-of-16"),
                result.prob_reach(team_id, "quarterfinals"),
                result.prob_reach(team_id, "semifinals"),
                result.prob_reach(team_id, "final"),
                result.prob_champion(team_id),
            )
        )
    rows.sort(key=lambda r: -r[5])

    print(f"\n=== FIFA World Cup 2026 — knockout Monte Carlo ({result.n_trajectories} trajectories) ===")
    print(f"{'Team':<16}{'R16':>8}{'QF':>8}{'SF':>8}{'F':>8}{'Champ':>9}")
    for name, r16, qf, sf, f, champ in rows:
        print(f"{name:<16}{r16*100:>7.1f}%{qf*100:>7.1f}%{sf*100:>7.1f}%{f*100:>7.1f}%{champ*100:>8.1f}%")

    if not args.no_save:
        append_snapshot(result)
        print(f"\nSnapshot appended to {DEFAULT_HISTORY_PATH}")
    return 0


def cmd_bracket(args):
    snapshot = build_snapshot()
    print("\n=== Current bracket state (from ESPN, live) ===")
    for slug in ["round-of-32", "round-of-16", "quarterfinals", "semifinals", "3rd-place-match", "final"]:
        matches = snapshot.bracket.matches_by_round.get(slug, [])
        if not matches:
            continue
        print(f"\n-- {ROUND_LABELS.get(slug, slug)} --")
        for m in matches:
            h = m.home.team_name or "TBD"
            a = m.away.team_name or "TBD"
            state = m.status_description
            score = f"{m.home.score}-{m.away.score}" if m.home.score is not None else ""
            print(f"  [{m.slot}] {h} vs {a}  {score}  ({state})")
    return 0


def build_parser() -> argparse.ArgumentParser:
    sim_args = argparse.ArgumentParser(add_help=False)
    sim_args.add_argument("--n", type=int, default=10000, help="number of Monte Carlo trajectories (default 10000)")
    sim_args.add_argument("--seed", type=int, default=None, help="random seed (default: nondeterministic)")

    p = argparse.ArgumentParser(prog="fifa_sim", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="command", required=True)

    p_team = sub.add_parser("team", parents=[sim_args], help="show one team's knockout-stage probabilities")
    p_team.add_argument("name", help="team name, e.g. Brazil")
    p_team.add_argument("--plot", action="store_true", help="also render a probability-over-time chart")
    p_team.add_argument("--no-save", action="store_true", help="don't append this run to history")
    p_team.set_defaults(func=cmd_team)

    p_sim = sub.add_parser("simulate", parents=[sim_args], help="run the full 32-team simulation and print a leaderboard")
    p_sim.add_argument("--no-save", action="store_true", help="don't append this run to history")
    p_sim.set_defaults(func=cmd_simulate)

    p_bracket = sub.add_parser("bracket", help="print the current bracket state (no simulation)")
    p_bracket.set_defaults(func=cmd_bracket)

    return p


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
