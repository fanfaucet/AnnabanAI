#!/usr/bin/env python3
"""Mission Control Live Feed Simulator for a multi-node space mission."""

from __future__ import annotations

import argparse
import json
import random
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Dict, List, Optional


class Priority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class CommentStatus(str, Enum):
    NEW = "NEW"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    IN_REVIEW = "IN_REVIEW"
    RESOLVED = "RESOLVED"


class ActionType(str, Enum):
    AUTO_CORRECT = "AUTO_CORRECT"
    MONITOR = "MONITOR"
    DISPATCH_DRONE = "DISPATCH_DRONE"
    HANDLE_HUMAN_REVIEW = "HANDLE_HUMAN_REVIEW"


class VoteChoice(str, Enum):
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    ABSTAIN = "ABSTAIN"


@dataclass
class Telemetry:
    power_kw: float
    fuel_pct: float
    thermal_c: float
    comms_latency_ms: int
    radiation_msv: float
    oxygen_pct: Optional[float] = None
    co2_ppm: Optional[int] = None
    pressure_kpa: Optional[float] = None


@dataclass
class SubsystemState:
    propulsion: str
    comms: str
    navigation: str
    life_support: str
    eclss_handover: str
    crew_ingress: str
    power_node_mode: str


@dataclass
class NodeState:
    node_id: str
    name: str
    node_type: str
    telemetry: Telemetry
    subsystems: SubsystemState
    anomalies: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)


@dataclass
class ExternalComment:
    comment_id: str
    source: str
    author: str
    timestamp_utc: str
    priority: Priority
    target_nodes: List[str]
    status: CommentStatus
    linked_actions: List[ActionType]
    content: str
    ai_council_response: Optional[str] = None


@dataclass
class CouncilVote:
    role: str
    opinion: str
    vote: VoteChoice
    preferred_action: ActionType


@dataclass
class CouncilEvent:
    event_id: str
    trigger_type: str
    trigger_ref_id: str
    timestamp_utc: str
    target_nodes: List[str]
    votes: List[CouncilVote]
    decision: ActionType
    human_review_required: bool
    rationale: str


@dataclass
class LedgerEntry:
    entry_id: str
    timestamp_utc: str
    entry_type: str
    reference_id: str
    details: str


class MissionControlSimulator:
    def __init__(self, seed: int = 42):
        random.seed(seed)
        self.start_time = datetime.now(timezone.utc)
        self.elapsed = timedelta()
        self.nodes = self._init_nodes()
        self.comment_log: List[ExternalComment] = []
        self.council_log: List[CouncilEvent] = []
        self.ledger: List[LedgerEntry] = []
        self.step_counter = 0

    def _init_nodes(self) -> Dict[str, NodeState]:
        return {
            "STARSHIP": NodeState(
                node_id="STARSHIP",
                name="Starship Transit Vehicle",
                node_type="CREWED_VEHICLE",
                telemetry=Telemetry(920.0, 78.0, 33.2, 190, 1.8, oxygen_pct=20.8, co2_ppm=740, pressure_kpa=100.8),
                subsystems=SubsystemState("NOMINAL", "NOMINAL", "NOMINAL", "STABLE", "PENDING", "DOCKING_PREP", "BATTERY_ASSIST"),
                dependencies=["ISS", "LUNAR_ORBITER"],
            ),
            "ISS": NodeState(
                node_id="ISS",
                name="International Space Station",
                node_type="ORBITAL_HABITAT",
                telemetry=Telemetry(1140.0, 65.0, 24.5, 120, 0.9, oxygen_pct=21.0, co2_ppm=680, pressure_kpa=101.2),
                subsystems=SubsystemState("N/A", "NOMINAL", "NOMINAL", "STABLE", "RECEIVING_CONTROL", "AIRLOCK_READY", "SOLAR_PRIMARY"),
                dependencies=["STARSHIP", "ISOTOPE_NODE_A"],
            ),
            "LUNAR_ORBITER": NodeState(
                node_id="LUNAR_ORBITER",
                name="Lunar Relay Orbiter",
                node_type="RELAY_SAT",
                telemetry=Telemetry(410.0, 54.0, -12.0, 310, 2.6),
                subsystems=SubsystemState("MICRO_THRUSTERS_OK", "DEGRADED", "NOMINAL", "N/A", "N/A", "N/A", "FUEL_CELL_BACKUP"),
                anomalies=["relay_packet_loss_3pct"],
                dependencies=["STARSHIP", "MARS_OUTPOST"],
            ),
            "MARS_OUTPOST": NodeState(
                node_id="MARS_OUTPOST",
                name="Mars Surface Outpost",
                node_type="SURFACE_BASE",
                telemetry=Telemetry(1320.0, 82.0, -45.0, 870, 3.9, oxygen_pct=19.8, co2_ppm=920, pressure_kpa=89.4),
                subsystems=SubsystemState("N/A", "HIGH_LATENCY", "NOMINAL", "STRESS_TEST", "N/A", "CREW_SAFE", "REACTOR_LINKED"),
                dependencies=["ISOTOPE_NODE_A", "LUNAR_ORBITER"],
            ),
            "ISOTOPE_NODE_A": NodeState(
                node_id="ISOTOPE_NODE_A",
                name="Buried Isotope Power Node A",
                node_type="NUCLEAR_ISOTOPE_NODE",
                telemetry=Telemetry(560.0, 100.0, 72.0, 430, 8.4),
                subsystems=SubsystemState("N/A", "NOMINAL", "N/A", "N/A", "N/A", "N/A", "ISOTOPE_REGULATION"),
                dependencies=["ISS", "MARS_OUTPOST"],
            ),
        }

    def _now_iso(self) -> str:
        return (self.start_time + self.elapsed).isoformat()

    def _mission_clock(self) -> str:
        total_seconds = int(self.elapsed.total_seconds())
        hh = total_seconds // 3600
        mm = (total_seconds % 3600) // 60
        ss = total_seconds % 60
        return f"T+{hh:02}:{mm:02}:{ss:02}"

    def _next_id(self, prefix: str) -> str:
        self.step_counter += 1
        return f"{prefix}-{self.step_counter:04d}"

    def _append_ledger(self, entry_type: str, reference_id: str, details: str) -> None:
        self.ledger.append(
            LedgerEntry(
                entry_id=self._next_id("LEDGER"),
                timestamp_utc=self._now_iso(),
                entry_type=entry_type,
                reference_id=reference_id,
                details=details,
            )
        )

    def _update_telemetry(self) -> None:
        for node in self.nodes.values():
            node.telemetry.power_kw = round(node.telemetry.power_kw + random.uniform(-8.0, 6.0), 2)
            node.telemetry.thermal_c = round(node.telemetry.thermal_c + random.uniform(-1.3, 1.1), 2)
            node.telemetry.comms_latency_ms = max(50, int(node.telemetry.comms_latency_ms + random.randint(-20, 25)))
            node.telemetry.radiation_msv = round(max(0.2, node.telemetry.radiation_msv + random.uniform(-0.2, 0.35)), 2)
            if node.telemetry.oxygen_pct is not None:
                node.telemetry.oxygen_pct = round(node.telemetry.oxygen_pct + random.uniform(-0.15, 0.08), 2)
            if node.telemetry.co2_ppm is not None:
                node.telemetry.co2_ppm = max(350, int(node.telemetry.co2_ppm + random.randint(-35, 40)))

    def _register_comment(
        self,
        source: str,
        author: str,
        priority: Priority,
        target_nodes: List[str],
        linked_actions: List[ActionType],
        content: str,
    ) -> ExternalComment:
        comment = ExternalComment(
            comment_id=self._next_id("CMT"),
            source=source,
            author=author,
            timestamp_utc=self._now_iso(),
            priority=priority,
            target_nodes=target_nodes,
            status=CommentStatus.NEW,
            linked_actions=linked_actions,
            content=content,
        )
        self.comment_log.append(comment)
        self._append_ledger("COMMENT", comment.comment_id, f"{source} -> {','.join(target_nodes)} | {content}")
        return comment

    def _deliberate(self, trigger_type: str, trigger_ref_id: str, target_nodes: List[str], context: str) -> CouncilEvent:
        candidate_actions = [ActionType.MONITOR, ActionType.AUTO_CORRECT, ActionType.DISPATCH_DRONE, ActionType.HANDLE_HUMAN_REVIEW]
        votes: List[CouncilVote] = []
        trigger_comment = next((comment for comment in self.comment_log if comment.comment_id == trigger_ref_id), None)
        priority = trigger_comment.priority if trigger_comment else Priority.MEDIUM
        available_actions = set(trigger_comment.linked_actions) if trigger_comment else set(candidate_actions)
        if not available_actions:
            available_actions = set(candidate_actions)

        context_lower = context.lower()
        target_set = set(target_nodes)
        autonomy_bias = 0
        if "relay" in context_lower or "comms" in context_lower or "autonomy" in context_lower or "authorize" in context_lower or "correction" in context_lower:
            autonomy_bias += 1
        if "monitor" in context_lower or "visibility" in context_lower or priority == Priority.LOW:
            autonomy_bias -= 1
        high_consequence = (
            priority in {Priority.HIGH, Priority.CRITICAL}
            or "safety critical" in context_lower
            or "director oversight" in context_lower
            or "human-reviewed" in context_lower
            or ("isotope" in context_lower and "ISOTOPE_NODE_A" in target_set)
        )
        drone_scenario = "inspection" in context_lower or "anomaly" in context_lower or "MARS_OUTPOST" in target_set

        role_profiles = {
            "Analyst": {
                "opinion": "Data trend indicates escalating risk envelope.",
                "choices": [ActionType.AUTO_CORRECT, ActionType.MONITOR, ActionType.HANDLE_HUMAN_REVIEW],
            },
            "Guardian": {
                "opinion": "Crew and infrastructure safety margin is primary.",
                "choices": [ActionType.HANDLE_HUMAN_REVIEW, ActionType.MONITOR, ActionType.AUTO_CORRECT],
            },
            "Ethicist": {
                "opinion": "Bias toward transparent oversight on high-impact changes.",
                "choices": [ActionType.MONITOR, ActionType.HANDLE_HUMAN_REVIEW, ActionType.AUTO_CORRECT],
            },
            "Innovator": {
                "opinion": "Rapid mitigation with bounded autonomy is viable.",
                "choices": [ActionType.DISPATCH_DRONE, ActionType.AUTO_CORRECT, ActionType.MONITOR],
            },
        }

        action_counts: Dict[ActionType, int] = {action: 0 for action in candidate_actions}
        for role, profile in role_profiles.items():
            ranked_actions = list(profile["choices"])
            if role == "Analyst":
                ranked_actions = [ActionType.AUTO_CORRECT, ActionType.MONITOR, ActionType.HANDLE_HUMAN_REVIEW]
                if high_consequence:
                    ranked_actions.insert(0, ActionType.HANDLE_HUMAN_REVIEW)
                elif autonomy_bias < 0:
                    ranked_actions.insert(0, ActionType.MONITOR)
            elif role == "Guardian":
                ranked_actions = [ActionType.HANDLE_HUMAN_REVIEW, ActionType.MONITOR, ActionType.AUTO_CORRECT]
                if autonomy_bias > 0 and not high_consequence and ActionType.AUTO_CORRECT in available_actions:
                    ranked_actions = [ActionType.AUTO_CORRECT, ActionType.MONITOR, ActionType.HANDLE_HUMAN_REVIEW]
                elif autonomy_bias < 0:
                    ranked_actions.insert(0, ActionType.MONITOR)
            elif role == "Ethicist":
                ranked_actions = [ActionType.MONITOR, ActionType.HANDLE_HUMAN_REVIEW, ActionType.AUTO_CORRECT]
                if high_consequence:
                    ranked_actions.insert(0, ActionType.HANDLE_HUMAN_REVIEW)
                elif autonomy_bias > 0 and ActionType.AUTO_CORRECT in available_actions:
                    ranked_actions = [ActionType.AUTO_CORRECT, ActionType.MONITOR, ActionType.HANDLE_HUMAN_REVIEW]
            elif role == "Innovator":
                ranked_actions = [ActionType.DISPATCH_DRONE, ActionType.AUTO_CORRECT, ActionType.MONITOR]
                if not drone_scenario:
                    ranked_actions = [ActionType.AUTO_CORRECT, ActionType.MONITOR, ActionType.DISPATCH_DRONE]
                if high_consequence:
                    ranked_actions.append(ActionType.HANDLE_HUMAN_REVIEW)

            preferred = next((action for action in ranked_actions if action in available_actions), ActionType.MONITOR)
            vote_choice = VoteChoice.ABSTAIN if preferred == ActionType.MONITOR else VoteChoice.APPROVE
            votes.append(CouncilVote(role=role, opinion=profile["opinion"], vote=vote_choice, preferred_action=preferred))
            action_counts[preferred] += 1

        decision = max(candidate_actions, key=lambda action: (action_counts[action], -candidate_actions.index(action)))
        human_review_required = high_consequence or decision == ActionType.HANDLE_HUMAN_REVIEW

        event = CouncilEvent(
            event_id=self._next_id("COUNCIL"),
            trigger_type=trigger_type,
            trigger_ref_id=trigger_ref_id,
            timestamp_utc=self._now_iso(),
            target_nodes=target_nodes,
            votes=votes,
            decision=decision,
            human_review_required=human_review_required,
            rationale=context,
        )
        self.council_log.append(event)
        self._append_ledger(
            "COUNCIL_DECISION",
            event.event_id,
            f"Decision={event.decision.value}; human_review={event.human_review_required}; targets={','.join(target_nodes)}",
        )
        return event

    def _apply_action(self, event: CouncilEvent) -> None:
        for node_id in event.target_nodes:
            node = self.nodes[node_id]
            if event.decision == ActionType.AUTO_CORRECT and "relay_packet_loss_3pct" in node.anomalies:
                node.anomalies.remove("relay_packet_loss_3pct")
                node.subsystems.comms = "RECOVERING"
                self._append_ledger("ACTION", event.event_id, f"{node_id} relay correction command uploaded")
            elif event.decision == ActionType.DISPATCH_DRONE:
                node.subsystems.navigation = "DRONE_ASSIST_ACTIVE"
                self._append_ledger("ACTION", event.event_id, f"{node_id} autonomous drone dispatched for inspection")
            elif event.decision == ActionType.HANDLE_HUMAN_REVIEW:
                node.subsystems.comms = "AWAITING_HUMAN_REVIEW"
                self._append_ledger("ACTION", event.event_id, f"{node_id} queued for mission director approval")
            else:
                node.subsystems.comms = "MONITORING"
                self._append_ledger("ACTION", event.event_id, f"{node_id} placed under enhanced monitoring")

    def _simulate_eclss_handover(self) -> None:
        starship = self.nodes["STARSHIP"]
        iss = self.nodes["ISS"]
        starship.subsystems.crew_ingress = "CREW_TRANSFER_ACTIVE"
        starship.subsystems.eclss_handover = "HANDOVER_TO_ISS"
        iss.subsystems.crew_ingress = "CREW_RECEIVING"
        iss.subsystems.eclss_handover = "ASSUMED_PRIMARY"
        starship.telemetry.co2_ppm = max(500, int(starship.telemetry.co2_ppm - 90))
        iss.telemetry.co2_ppm = int(iss.telemetry.co2_ppm + 70)
        self._append_ledger("STATE_CHANGE", "ECLSS-TRANSFER", "Starship -> ISS ECLSS handover during crew ingress")

    def _simulate_isotope_anomaly(self) -> None:
        isotope = self.nodes["ISOTOPE_NODE_A"]
        mars = self.nodes["MARS_OUTPOST"]
        anomaly = "thermal_spike_isotope_vault"
        if anomaly not in isotope.anomalies:
            isotope.anomalies.append(anomaly)
        mars.anomalies.append("power_bus_fluctuation_from_isotope_node")
        isotope.telemetry.thermal_c = round(isotope.telemetry.thermal_c + 8.5, 2)
        mars.telemetry.power_kw = round(mars.telemetry.power_kw - 45.0, 2)
        self._append_ledger("ANOMALY", "ISOTOPE_NODE_A", "Thermal spike propagated to Mars outpost power bus")

    def payload(self, recent_comments: List[ExternalComment], recent_council: List[CouncilEvent], recent_ledger: List[LedgerEntry]) -> Dict:
        return {
            "mission_time": self._mission_clock(),
            "nodes": [asdict(node) for node in self.nodes.values()],
            "comments": [asdict(c) for c in recent_comments],
            "council_events": [asdict(c) for c in recent_council],
            "ledger_entries": [asdict(l) for l in recent_ledger],
        }

    def run(self, realtime: bool = False, interval: float = 0.8) -> None:
        # Step 1: baseline telemetry update
        self.elapsed += timedelta(seconds=20)
        self._update_telemetry()
        print(json.dumps(self.payload([], [], self.ledger[-1:] if self.ledger else []), indent=2, default=str))
        if realtime:
            time.sleep(interval)

        # Step 2: cross-node relay concern comment
        self.elapsed += timedelta(seconds=25)
        comment_1 = self._register_comment(
            source="NASA",
            author="Flight Dynamics",
            priority=Priority.MEDIUM,
            target_nodes=["LUNAR_ORBITER", "STARSHIP"],
            linked_actions=[ActionType.MONITOR, ActionType.AUTO_CORRECT],
            content="Detected relay packet loss impacting Starship guidance sync; assess corrective upload.",
        )
        council_1 = self._deliberate("COMMENT", comment_1.comment_id, comment_1.target_nodes, "Cross-node comms degradation should be corrected quickly.")
        comment_1.status = CommentStatus.IN_REVIEW
        comment_1.ai_council_response = f"Council decision: {council_1.decision.value}"
        self._apply_action(council_1)
        print(json.dumps(self.payload([comment_1], [council_1], self.ledger[-4:]), indent=2, default=str))
        if realtime:
            time.sleep(interval)

        # Step 3: ECLSS handover during crew ingress
        self.elapsed += timedelta(seconds=30)
        self._simulate_eclss_handover()
        comment_2 = self._register_comment(
            source="SpaceX Ops",
            author="Habitat Controller",
            priority=Priority.HIGH,
            target_nodes=["STARSHIP", "ISS"],
            linked_actions=[ActionType.MONITOR],
            content="Crew ingress confirmed. Verify ECLSS handover and atmospheric stabilization across docking interface.",
        )
        council_2 = self._deliberate("COMMENT", comment_2.comment_id, comment_2.target_nodes, "ECLSS transition is safety critical; maintain human visibility.")
        comment_2.status = CommentStatus.ACKNOWLEDGED
        comment_2.ai_council_response = "Council recommends monitoring while handover remains within thresholds."
        self._apply_action(council_2)
        print(json.dumps(self.payload([comment_2], [council_2], self.ledger[-5:]), indent=2, default=str))
        if realtime:
            time.sleep(interval)

        # Step 4: isotope node anomaly causes multi-node effects
        self.elapsed += timedelta(seconds=35)
        self._update_telemetry()
        self._simulate_isotope_anomaly()
        comment_3 = self._register_comment(
            source="ESA",
            author="Deep Power Desk",
            priority=Priority.CRITICAL,
            target_nodes=["ISOTOPE_NODE_A", "MARS_OUTPOST", "ISS"],
            linked_actions=[ActionType.DISPATCH_DRONE, ActionType.HANDLE_HUMAN_REVIEW],
            content="Buried isotope thermal spike detected with downstream power fluctuations; request immediate mitigation and director oversight.",
        )
        council_3 = self._deliberate("ANOMALY", comment_3.comment_id, comment_3.target_nodes, "Isotope event has high consequence, requires human-reviewed mitigation.")
        comment_3.status = CommentStatus.IN_REVIEW
        comment_3.ai_council_response = f"Council escalated to {council_3.decision.value}; human review required={council_3.human_review_required}."
        self._apply_action(council_3)
        print(json.dumps(self.payload([comment_3], [council_3], self.ledger[-6:]), indent=2, default=str))
        if realtime:
            time.sleep(interval)

        # Step 5: mission director follow-up for mixed autonomy
        self.elapsed += timedelta(seconds=40)
        comment_4 = self._register_comment(
            source="Mission Director",
            author="Director K. Sato",
            priority=Priority.LOW,
            target_nodes=["MARS_OUTPOST", "LUNAR_ORBITER"],
            linked_actions=[ActionType.AUTO_CORRECT, ActionType.HANDLE_HUMAN_REVIEW],
            content="Authorize autonomous correction for relay routing; retain human sign-off for isotope thermal management changes.",
        )
        council_4 = self._deliberate("COMMENT", comment_4.comment_id, comment_4.target_nodes, "Blend autonomy for relay systems with oversight for isotope remediation.")
        comment_4.status = CommentStatus.RESOLVED
        comment_4.ai_council_response = "Council accepted split posture: auto-correct comms path, human review for power core updates."
        self._apply_action(council_4)
        print(json.dumps(self.payload([comment_4], [council_4], self.ledger[-5:]), indent=2, default=str))
        if realtime:
            time.sleep(interval)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Simulate mission control live feed JSON payloads.")
    parser.add_argument("--realtime", action="store_true", help="Sleep between payload outputs.")
    parser.add_argument("--interval", type=float, default=0.8, help="Seconds between payloads when --realtime is enabled.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for deterministic telemetry drift.")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    sim = MissionControlSimulator(seed=args.seed)
    sim.run(realtime=args.realtime, interval=args.interval)
