from whylab.domain.models import EvidenceRule, Observation
from whylab.reasoning.rules import EvidenceDirection, EvidenceRuleResult


def evaluate_evidence_rule(
    rule: EvidenceRule,
    observation: Observation,
) -> EvidenceRuleResult:
    """Evaluate one machine-readable evidence rule against an observation."""

    if observation.variable != rule.variable:
        return EvidenceRuleResult(
            direction=EvidenceDirection.NEUTRAL,
            reason="Observation does not match this rule's variable.",
        )

    if rule.unit is not None and observation.unit != rule.unit:
        return EvidenceRuleResult(
            direction=EvidenceDirection.NEUTRAL,
            reason="Observation unit does not match this rule.",
        )

    try:
        matched = _compare(
            observation.value,
            rule.operator.value,
            rule.value,
        )
    except TypeError:
        return EvidenceRuleResult(
            direction=EvidenceDirection.NEUTRAL,
            reason="Observation value cannot be compared with this rule.",
        )

    if not matched:
        return EvidenceRuleResult(
            direction=EvidenceDirection.NEUTRAL,
            reason="Observation does not satisfy this evidence rule.",
        )

    return EvidenceRuleResult(
        direction=EvidenceDirection(rule.effect.value),
        reason=rule.reason,
    )


def _compare(
    observed: str | int | float | bool,
    operator: str,
    expected: str | int | float | bool,
) -> bool:
    if operator == "==":
        return observed == expected

    if operator == "!=":
        return observed != expected

    if (
        isinstance(observed, bool)
        or isinstance(expected, bool)
        or not isinstance(observed, (int, float))
        or not isinstance(expected, (int, float))
    ):
        raise TypeError("Ordered comparisons require numeric values.")

    if operator == "<":
        return observed < expected

    if operator == "<=":
        return observed <= expected

    if operator == ">":
        return observed > expected

    if operator == ">=":
        return observed >= expected

    raise ValueError(f"Unsupported comparison operator: {operator}")
