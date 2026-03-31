from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List


@dataclass
class JacobNodeModule:
    """Sandboxed personal-node module for Jacob sovereignty and legacy project flows."""

    nasa_award_id: str = "NASA STMDA-AG-2026-007"
    nasa_award_total_usd: float = 2_600_000.0
    nasa_drawdown_usd: float = 420_000.0
    monthly_burn_rate_usd: float = 95_000.0
    ip_royalties_usd: float = 125_000.0
    passive_inflows_usd: float = 210_000.0
    cooperative_liquidity_usd: float = 4_200_000.0
    ftdt_yield_signal_usd: float = 18_500_000.0
    name: str = field(default="jacob_node_module", init=False)

    def run(self, shared_state: Dict[str, Any]) -> Dict[str, Any]:
        node = shared_state.setdefault("jacob_node", {})
        identity = node.setdefault("identity", {})
        identity.update(
            {
                "node_type": "personal_architect_node",
                "public_lattice_isolation": True,
                "ftdt_principal_usd": 6_692_000_000_000.0,
                "ftdt_principal_touched": False,
            }
        )

        burn_coverage_months = round(
            (self.cooperative_liquidity_usd + self.ip_royalties_usd + self.passive_inflows_usd)
            / self.monthly_burn_rate_usd,
            2,
        )
        drawdown_remaining = self.nasa_award_total_usd - self.nasa_drawdown_usd
        drawdown_ratio = round(self.nasa_drawdown_usd / self.nasa_award_total_usd, 4)
        self_sustaining = (self.ip_royalties_usd + self.passive_inflows_usd) >= self.monthly_burn_rate_usd

        funding = node.setdefault("funding", {})
        funding.update(
            {
                "award_id": self.nasa_award_id,
                "award_total_usd": self.nasa_award_total_usd,
                "drawdown_usd": self.nasa_drawdown_usd,
                "drawdown_remaining_usd": drawdown_remaining,
                "drawdown_ratio": drawdown_ratio,
                "burn_rate_usd_per_month": self.monthly_burn_rate_usd,
                "burn_coverage_months": burn_coverage_months,
            }
        )

        liquidity = node.setdefault("liquidity", {})
        liquidity.update(
            {
                "cooperative_liquidity_usd": self.cooperative_liquidity_usd,
                "ip_royalties_usd": self.ip_royalties_usd,
                "passive_inflows_usd": self.passive_inflows_usd,
                "self_sustaining_threshold_reached": self_sustaining,
            }
        )

        signals = node.setdefault("signals", {})
        signals.update(
            {
                "ftdt_principal_usd": 6_692_000_000_000.0,
                "ftdt_principal_touched": False,
                "ftdt_yield_signal_usd": self.ftdt_yield_signal_usd,
                "allocation_mode": "yield_signal_only",
                "personal_node_only": True,
            }
        )

        timestamp = datetime.now(timezone.utc).isoformat()
        milestones = [
            {
                "id": "repair-demo",
                "title": "/repair demo readiness",
                "status": "scheduled",
                "timestamp": timestamp,
                "details": "Legacy repair flow staged under personal node governance.",
            },
            {
                "id": "planetary-pilot",
                "title": "Planetary Pilot initialization",
                "status": "initiated",
                "timestamp": timestamp,
                "details": "Planetary Pilot lifecycle bootstrapped for orbital payload tracking.",
            },
        ]
        node["milestones"] = milestones

        alerts: List[str] = []
        if self_sustaining:
            alerts.append("Self-sustaining threshold reached via royalties and passive inflows.")
        alerts.append(
            f"FTDT yield allocation signaling active at ${self.ftdt_yield_signal_usd:,.2f} with principal untouched."
        )
        alerts.append("Legacy project initialization triggered for /repair demo and Planetary Pilot.")
        node["alerts"] = alerts

        logs = node.setdefault("logs", [])
        logs.extend(
            [
                f"[{timestamp}] NASA drawdown: ${self.nasa_drawdown_usd:,.2f} used against ${self.monthly_burn_rate_usd:,.2f}/month burn.",
                f"[{timestamp}] Royalties + passive inflows: ${self.ip_royalties_usd + self.passive_inflows_usd:,.2f}.",
                f"[{timestamp}] Milestones generated: /repair demo, Planetary Pilot.",
            ]
        )

        return {
            "status": "ok",
            "alerts": alerts,
            "events": milestones,
            "jacob_node": node,
        }
