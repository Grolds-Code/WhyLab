from dataclasses import dataclass
from enum import StrEnum

from whylab.domain.models import Observation


class EvidenceDirection(StrEnum):
    """How an observation affects a hypothesis."""

    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    NEUTRAL = "neutral"


@dataclass(frozen=True)
class EvidenceRuleResult:
    """Result of applying a deterministic evidence rule."""

    direction: EvidenceDirection
    reason: str


def evaluate_soil_moisture_for_underwatering(
    observation: Observation,
) -> EvidenceRuleResult:
    """Interpret soil-moisture evidence for an underwatering hypothesis."""

    if observation.variable != "soil_moisture":
        return EvidenceRuleResult(
            direction=EvidenceDirection.NEUTRAL,
            reason="Observation is not about soil moisture.",
        )

    if not isinstance(observation.value, (int, float)):
        return EvidenceRuleResult(
            direction=EvidenceDirection.NEUTRAL,
            reason="Soil-moisture value is not numeric.",
        )

    if observation.value >= 60:
        return EvidenceRuleResult(
            direction=EvidenceDirection.CONTRADICTS,
            reason="Relatively moist soil weakens the underwatering explanation.",
        )

    if observation.value <= 30:
        return EvidenceRuleResult(
            direction=EvidenceDirection.SUPPORTS,
            reason="Low soil moisture is consistent with underwatering.",
        )

    return EvidenceRuleResult(
        direction=EvidenceDirection.NEUTRAL,
        reason="Soil moisture is intermediate and does not strongly distinguish the hypothesis.",
    )
