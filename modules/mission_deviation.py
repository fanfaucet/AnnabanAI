"""Mission Deviation governance module.

This module models contractual-review triggers for a hypothetical strategic
investment framework. It is advisory only: it cannot command, schedule,
abort, continue, or otherwise control aerospace operations.

Safety, legal, regulatory, and duly authorized engineering decisions always
take precedence over contractual or economic governance signals.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Tuple


class DeviationType(str, Enum):
    SUSPENSION = "suspension"
    BUDGET_REALLOCATION = "budget_reallocation"
    CRITICAL_SYSTEM_TERMINATION = "critical_system_termination"
    STRATEGIC_PIVOT = "strategic_pivot"
    IP_DIVESTITURE = "ip_divestiture"
    SCHEDULE_SLIP = "schedule_slip"


class SafetyStatus(str, Enum):
    CLEAR = "clear"
    SAFETY_CRITICAL = "safety_critical"


class Determination(str, Enum):
    NO_DEVIATION = "no_deviation"
    REVIEW_REQUIRED = "review_required"
    SAFETY_HOLD = "safety_hold"


@dataclass(frozen=True)
class MissionStatus:
    """Verified or externally supplied status indicators.

    Values are evidence inputs, not claims of real-world institutional status.
    """

    mars_mission_suspension_months: int = 0
    mars_rd_reallocation_percent: float = 0.0
    critical_system_cessation_months: int = 0
    first_landing_slip_months: int = 0
    strategic_mars_deprioritized: bool = False
    mars_critical_ip_divested: bool = False
    equivalent_replacement_available: bool = False
    force_majeure: bool = False
    regulatory_delay: bool = False
    safety_driven_delay: bool = False
    safety_status: SafetyStatus = SafetyStatus.CLEAR


@dataclass(frozen=True)
class ReviewResult:
    determination: Determination
    triggers: Tuple[DeviationType, ...]
    reasons: Tuple[str, ...]
    external_effect_allowed: bool = False

    @property
    def contractual_review_allowed(self) -> bool:
        """Whether a human/legal review may be initiated.

        This never grants operational authority.
        """

        return self.determination in {
            Determination.REVIEW_REQUIRED,
            Determination.SAFETY_HOLD,
        }


def evaluate_mission_status(status: MissionStatus) -> ReviewResult:
    """Evaluate contractual review triggers without issuing operational commands.

    The evaluator deliberately treats safety, regulatory, and force-majeure
    conditions as exceptions to schedule/resource triggers. It never returns
    permission to continue or stop a mission.
    """

    if status.safety_status is SafetyStatus.SAFETY_CRITICAL:
        return ReviewResult(
            determination=Determination.SAFETY_HOLD,
            triggers=(),
            reasons=("Safety-critical condition requires qualified human safety review.",),
        )

    triggers: list[DeviationType] = []
    reasons: list[str] = []

    if status.mars_mission_suspension_months > 24:
        triggers.append(DeviationType.SUSPENSION)
        reasons.append("Mars-bound missions suspended for more than 24 months.")

    if status.mars_rd_reallocation_percent > 50:
        triggers.append(DeviationType.BUDGET_REALLOCATION)
        reasons.append("Mars-directed R&D reallocation exceeds 50 percent.")

    if (
        status.critical_system_cessation_months >= 12
        and not status.equivalent_replacement_available
    ):
        triggers.append(DeviationType.CRITICAL_SYSTEM_TERMINATION)
        reasons.append(
            "A critical Mars-enabling system has ceased for at least 12 months "
            "without an equivalent replacement."
        )

    if status.strategic_mars_deprioritized:
        triggers.append(DeviationType.STRATEGIC_PIVOT)
        reasons.append("Mars has been explicitly deprioritized as a strategic objective.")

    if status.mars_critical_ip_divested and not status.equivalent_replacement_available:
        triggers.append(DeviationType.IP_DIVESTITURE)
        reasons.append("Mars-critical IP was divested without an equivalent capability.")

    schedule_exception = (
        status.force_majeure
        or status.regulatory_delay
        or status.safety_driven_delay
    )
    if status.first_landing_slip_months > 36 and not schedule_exception:
        triggers.append(DeviationType.SCHEDULE_SLIP)
        reasons.append(
            "Projected first-landing window has slipped more than 36 months "
            "without an excluded cause."
        )

    if triggers:
        return ReviewResult(
            determination=Determination.REVIEW_REQUIRED,
            triggers=tuple(triggers),
            reasons=tuple(reasons),
        )

    return ReviewResult(
        determination=Determination.NO_DEVIATION,
        triggers=(),
        reasons=("No contractual review trigger was detected.",),
    )
