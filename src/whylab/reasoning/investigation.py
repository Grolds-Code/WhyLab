from datetime import datetime, timezone

from whylab.domain.models import Investigation, Observation
from whylab.reasoning.evidence import apply_rule_result
from whylab.reasoning.falsification import check_underwatering_falsifier
from whylab.reasoning.rules import (
    evaluate_soil_moisture_for_root_stress,
    evaluate_soil_moisture_for_underwatering,
)


def apply_observation_to_investigation(
    investigation: Investigation,
    observation: Observation,
) -> Investigation:
    """Record an observation and update relevant hypotheses."""

    if observation in investigation.observations:
        return investigation

    investigation.observations.append(observation)

    for hypothesis in investigation.hypotheses:
        claim = hypothesis.claim.lower()

        if "underwater" in claim:
            rule_result = evaluate_soil_moisture_for_underwatering(observation)

            falsification_result = check_underwatering_falsifier(
                hypothesis,
                observation,
            )

            reason = (
                falsification_result.reason
                if falsification_result.triggered
                else rule_result.reason
            )

        elif "root stress" in claim or "excess water" in claim:
            rule_result = evaluate_soil_moisture_for_root_stress(observation)
            reason = rule_result.reason

        else:
            continue

        apply_rule_result(
            hypothesis=hypothesis,
            observation=observation,
            direction=rule_result.direction,
            reason=reason,
        )

    investigation.updated_at = datetime.now(timezone.utc)

    return investigation
