"""AnnabanAI Lattice Metrics: registry counts, explicitly sourced metrics, and history."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import json
from pathlib import Path
import random
import warnings
from typing import Any, Dict, List, Optional


@dataclass
class AgentSnapshot:
    total: int = 0
    active: int = 0
    by_role: Dict[str, int] = field(default_factory=dict)


@dataclass
class LatticeReport:
    lattice_expansion: float
    agent_activity: str
    stability: str
    joy_density: float
    thought_output_bandwidth: str
    human_sovereignty: float
    agent_counts: AgentSnapshot
    reflection: str
    timestamp: str
    metric_source: str = "synthetic"
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class LatticeMetrics:
    """Lightweight metrics tracker. Synthetic fields are not system measurements."""

    def __init__(
        self,
        history_file: str | Path = "data/lattice_history.json",
        seed: Optional[int] = None,
        max_history: int = 200,
    ) -> None:
        if isinstance(max_history, bool) or not isinstance(max_history, int) or max_history < 1:
            raise ValueError("max_history must be a positive integer")
        self._rng = random.Random(seed)
        self.history_file = Path(history_file)
        self.max_history = max_history
        self.history: List[LatticeReport] = []
        self._agent_registry: Dict[str, Dict[str, Any]] = {}
        self._load_history()

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    def register_agent(self, agent_id: str, role: str = "general", active: bool = True) -> None:
        if not agent_id or not agent_id.strip():
            raise ValueError("agent_id must be a non-empty string")
        self._agent_registry[agent_id] = {
            "role": role or "general",
            "active": bool(active),
            "registered_at": self._now(),
        }

    def set_agent_active(self, agent_id: str, active: bool) -> None:
        if agent_id not in self._agent_registry:
            raise KeyError(f"Unknown agent_id: {agent_id}")
        self._agent_registry[agent_id]["active"] = bool(active)

    def get_agent_counts(self) -> AgentSnapshot:
        total = len(self._agent_registry)
        active = sum(bool(a.get("active", False)) for a in self._agent_registry.values())
        by_role: Dict[str, int] = {}
        for meta in self._agent_registry.values():
            role = str(meta.get("role") or "general")
            by_role[role] = by_role.get(role, 0) + 1
        return AgentSnapshot(total=total, active=active, by_role=by_role)

    def _simulated_counts(self) -> AgentSnapshot:
        total = self._rng.randint(12, 48)
        active = self._rng.randint(int(total * 0.6), total)
        role_names = ["conversational", "task", "governance", "reflection"]
        role_counts = {role: 0 for role in role_names}
        for _ in range(total):
            role_counts[self._rng.choice(role_names)] += 1
        return AgentSnapshot(total=total, active=active, by_role=role_counts)

    def simulate(self, use_real_agents: bool = True) -> LatticeReport:
        use_registry = use_real_agents and bool(self._agent_registry)
        counts = self.get_agent_counts() if use_registry else self._simulated_counts()
        ratio = counts.active / counts.total if counts.total else 0.0
        activity = "high" if ratio >= 0.75 else "medium" if ratio >= 0.45 else "low"

        # These values remain synthetic until supplied by a defined measurement source.
        expansion = round(self._rng.uniform(35.0, 55.0), 1)
        joy = round(self._rng.uniform(0.88, 0.98), 2)
        sovereignty = round(self._rng.uniform(0.96, 0.995), 3)
        stability = "excellent" if expansion > 40 and joy > 0.90 and activity == "high" else "good"
        notes = ["Lattice expansion, joy density, sovereignty, and stability are synthetic demo values."]
        if not use_registry:
            notes.append("Agent counts are simulated, not discovered from a live agent runtime.")
        else:
            notes.append("Agent counts reflect this instance's in-memory registry only.")

        report = LatticeReport(
            lattice_expansion=expansion,
            agent_activity=activity,
            stability=stability,
            joy_density=joy,
            thought_output_bandwidth="unmeasured",
            human_sovereignty=sovereignty,
            agent_counts=counts,
            reflection="No automated interpretation should be treated as a verified system fact.",
            timestamp=self._now(),
            metric_source="synthetic" if not use_registry else "mixed: registry counts + synthetic quality metrics",
            notes=notes,
        )
        self._append_history(report)
        return report

    def _append_history(self, report: LatticeReport) -> None:
        self.history.append(report)
        self.history = self.history[-self.max_history:]
        self._save_history()

    def get_history(self, last_n: Optional[int] = None) -> List[LatticeReport]:
        if last_n is None:
            return list(self.history)
        if last_n < 0:
            raise ValueError("last_n must be >= 0")
        return self.history[-last_n:] if last_n else []

    def clear_history(self) -> None:
        self.history.clear()
        self._save_history()

    @staticmethod
    def _report_from_dict(item: Dict[str, Any]) -> LatticeReport:
        agent_data = item.get("agent_counts") or {}
        counts = AgentSnapshot(
            total=int(agent_data.get("total", 0)),
            active=int(agent_data.get("active", 0)),
            by_role=dict(agent_data.get("by_role", {})),
        )
        return LatticeReport(
            lattice_expansion=float(item["lattice_expansion"]),
            agent_activity=str(item["agent_activity"]),
            stability=str(item["stability"]),
            joy_density=float(item["joy_density"]),
            thought_output_bandwidth=str(item.get("thought_output_bandwidth", "unmeasured")),
            human_sovereignty=float(item["human_sovereignty"]),
            agent_counts=counts,
            reflection=str(item.get("reflection", "")),
            timestamp=str(item["timestamp"]),
            metric_source=str(item.get("metric_source", "legacy/unspecified")),
            notes=list(item.get("notes", [])),
        )

    def _load_history(self) -> None:
        if not self.history_file.exists():
            return
        try:
            data = json.loads(self.history_file.read_text(encoding="utf-8"))
            if not isinstance(data, list):
                raise ValueError("history root must be a JSON list")
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            warnings.warn(
                f"Could not load lattice history from {self.history_file}; original file was left untouched: {exc}",
                RuntimeWarning,
            )
            return
        loaded: List[LatticeReport] = []
        for index, item in enumerate(data):
            try:
                loaded.append(self._report_from_dict(item))
            except (KeyError, TypeError, ValueError) as exc:
                warnings.warn(f"Skipping malformed lattice history record {index}: {exc}", RuntimeWarning)
        self.history = loaded[-self.max_history:]

    def _save_history(self) -> None:
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps([r.to_dict() for r in self.history], indent=2)
        temp_path = self.history_file.with_suffix(self.history_file.suffix + ".tmp")
        temp_path.write_text(payload, encoding="utf-8")
        temp_path.replace(self.history_file)

    def print_report(self, report: Optional[LatticeReport] = None) -> None:
        report = report or self.simulate()
        print("AnnabanAI Lattice Metrics report")
        print(f"Source: {report.metric_source}")
        print(f"Lattice expansion: {report.lattice_expansion}% (synthetic unless externally measured)")
        print(f"Agent activity: {report.agent_activity}")
        print(f"Stability: {report.stability} (derived from synthetic demo fields)")
        print(f"Joy density: {report.joy_density:.0%} (synthetic proxy; not a validated metric)")
        print(f"Thought-output bandwidth: {report.thought_output_bandwidth}")
        print(f"Human sovereignty: {report.human_sovereignty:.1%} (synthetic unless instrumented)")
        print(f"Agents active/total: {report.agent_counts.active}/{report.agent_counts.total}")
        print(f"By role: {report.agent_counts.by_role}")
        print(f"Timestamp: {report.timestamp}")
        for note in report.notes:
            print(f"Note: {note}")

    def print_history_summary(self, last_n: int = 5) -> None:
        recent = self.get_history(last_n)
        if not recent:
            print("No history yet.")
            return
        print(f"Last {len(recent)} lattice snapshots:")
        for report in recent:
            counts = report.agent_counts
            print(
                f"[{report.timestamp}] source={report.metric_source} | "
                f"agents={counts.active}/{counts.total} | "
                f"expansion={report.lattice_expansion}% | "
                f"sovereignty={report.human_sovereignty:.1%}"
            )


if __name__ == "__main__":
    metrics = LatticeMetrics(seed=42)
    metrics.register_agent("cua_01", role="conversational", active=True)
    metrics.register_agent("task_07", role="task", active=True)
    metrics.register_agent("gov_03", role="governance", active=True)
    metrics.register_agent("reflect_02", role="reflection", active=False)
    metrics.register_agent("task_12", role="task", active=True)
    for _ in range(3):
        metrics.print_report(metrics.simulate(use_real_agents=True))
        print("-" * 60)
    metrics.print_history_summary()
