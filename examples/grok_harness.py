"""Grok Harness for AnnabanAI Lattice Metrics.

Demonstrates the in-memory agent registry and synthetic demo metrics.
It does not connect to or measure a live agent runtime.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import Optional

# Make the repository root importable when this file is run directly.
REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

try:
    from modules.lattice_metrics import LatticeMetrics, LatticeReport
except ImportError:  # Support running from a flat checkout/layout.
    from lattice_metrics import LatticeMetrics, LatticeReport


def seed_sample_agents(metrics: LatticeMetrics) -> None:
    """Register sample agents in this process's in-memory registry."""
    sample_agents = [
        ("cua_01", "conversational", True),
        ("cua_02", "conversational", True),
        ("task_07", "task", True),
        ("task_12", "task", True),
        ("task_15", "task", False),
        ("gov_03", "governance", True),
        ("gov_04", "governance", True),
        ("reflect_02", "reflection", False),
        ("reflect_05", "reflection", True),
    ]
    for agent_id, role, active in sample_agents:
        metrics.register_agent(agent_id, role=role, active=active)


def run_cycles(
    metrics: LatticeMetrics,
    cycles: int = 3,
    use_real_agents: bool = True,
    verbose: bool = True,
) -> list[LatticeReport]:
    """Run simulation cycles and return their reports."""
    if isinstance(cycles, bool) or not isinstance(cycles, int) or cycles < 1:
        raise ValueError("cycles must be an integer >= 1")
    reports: list[LatticeReport] = []
    for index in range(1, cycles + 1):
        if verbose:
            print("\n" + "=" * 64)
            print(f"Grok Harness — Cycle {index}/{cycles}")
            print("=" * 64)
        report = metrics.simulate(use_real_agents=use_real_agents)
        reports.append(report)
        if verbose:
            metrics.print_report(report)
    return reports


def print_final_summary(metrics: LatticeMetrics, reports: list[LatticeReport]) -> None:
    """Print a compact summary after a run."""
    print("\n" + "=" * 64)
    print("Grok Harness — Final Summary")
    print("=" * 64)
    print(f"Total cycles executed : {len(reports)}")
    print(f"History length        : {len(metrics.get_history())}")
    if reports:
        last = reports[-1]
        print(f"Last metrics source   : {last.metric_source}")
        print(f"Last active / total   : {last.agent_counts.active} / {last.agent_counts.total}")
    metrics.print_history_summary(last_n=min(5, len(reports)))


def main(
    cycles: int = 3,
    seed: Optional[int] = 42,
    history_file: str = "data/grok_harness_history.json",
    use_real_agents: bool = True,
    register_samples: bool = True,
) -> None:
    if isinstance(cycles, bool) or not isinstance(cycles, int) or cycles < 1:
        raise ValueError("cycles must be an integer >= 1")
    print("AnnabanAI × Grok Harness")
    print("Lattice Metrics evaluation runner")
    print("-" * 40)

    metrics = LatticeMetrics(
        history_file=Path(history_file),
        seed=seed,
        max_history=100,
    )
    if register_samples:
        seed_sample_agents(metrics)
        print(f"Registered {metrics.get_agent_counts().total} sample agents")

    reports = run_cycles(
        metrics,
        cycles=cycles,
        use_real_agents=use_real_agents,
        verbose=True,
    )
    print_final_summary(metrics, reports)
    print("\nHarness complete.")
    print("Agent counts come from this process's in-memory registry when enabled and populated.")
    print("Quality indicators (expansion, joy, sovereignty, stability) are synthetic demo values.")
    print("No live runtime telemetry is connected by this harness.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Grok Harness for AnnabanAI Lattice Metrics")
    parser.add_argument("--cycles", type=int, default=3, help="Number of simulation cycles (minimum 1)")
    parser.add_argument("--seed", type=int, default=42, help="RNG seed; default is deterministic")
    parser.add_argument("--random-seed", action="store_true", help="Use a non-deterministic RNG seed")
    parser.add_argument("--history", type=str, default="data/grok_harness_history.json",
                        help="Path for history JSON")
    parser.add_argument("--no-real-agents", action="store_true",
                        help="Force synthetic agent counts even if the registry is populated")
    parser.add_argument("--no-samples", action="store_true",
                        help="Do not register the sample agent set")
    args = parser.parse_args()

    main(
        cycles=args.cycles,
        seed=None if args.random_seed else args.seed,
        history_file=args.history,
        use_real_agents=not args.no_real_agents,
        register_samples=not args.no_samples,
    )
