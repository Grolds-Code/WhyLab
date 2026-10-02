from dataclasses import dataclass

from whylab.domain.models import Hypothesis, Observation
from whylab.reasoning.config import SoilMoistureRuleConfig


@dataclass(frozen=True)
class FalsificationResult:
    """Result of checking whether an observation weakens a hypothesis."""

    triggered: bool
    reason: str


def check_underwatering_falsifier(
    hypothesis: Hypothesis,
    observation: Observation,
    config: SoilMoistureRuleConfig | None = None,
) -> FalsificationResult:
    """Check whether moist soil weakens an underwatering hypothesis."""

    config = config or SoilMoistureRuleConfig()

    if "underwater" not in hypothesis.claim.lower():
        return FalsificationResult(
            triggered=False,
            reason="Hypothesis is not an underwatering explanation.",
        )

    if observation.variable != config.variable:
        return FalsificationResult(
            triggered=False,
            reason="Observation is not about soil moisture.",
        )

    if not isinstance(observation.value, (int, float)):
        return FalsificationResult(
            triggered=False,
            reason="Soil-moisture value is not numeric.",
        )

    if observation.value >= config.contradicts_underwatering_at_or_above:
        return FalsificationResult(
            triggered=True,
            reason=(
                "Persistently moist soil is inconsistent with the prediction "
                "that the plant is wilting because of insufficient water."
            ),
        )

    return FalsificationResult(
        triggered=False,
        reason="This observation does not falsify the underwatering hypothesis.",
    )
