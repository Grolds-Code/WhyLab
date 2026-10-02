from whylab.domain.models import EpistemicState, Hypothesis, Observation


def add_supporting_evidence(
    hypothesis: Hypothesis,
    observation: Observation,
    reason: str,
) -> Hypothesis:
    """Record an observation as evidence supporting a hypothesis."""

    evidence_entry = (
        f"{observation.variable}={observation.value}"
        f"{f' {observation.unit}' if observation.unit else ''}: {reason}"
    )

    hypothesis.evidence_for.append(evidence_entry)
    return hypothesis


def add_contradicting_evidence(
    hypothesis: Hypothesis,
    observation: Observation,
    reason: str,
) -> Hypothesis:
    """Record an observation as evidence against a hypothesis."""

    evidence_entry = (
        f"{observation.variable}={observation.value}"
        f"{f' {observation.unit}' if observation.unit else ''}: {reason}"
    )

    hypothesis.evidence_against.append(evidence_entry)
    return hypothesis


def update_epistemic_state(hypothesis: Hypothesis) -> Hypothesis:
    """Update a hypothesis state from its current evidence.

    This rule is intentionally conservative:
    mixed evidence remains OPEN, and KNOWN is never assigned automatically.
    """

    has_support = bool(hypothesis.evidence_for)
    has_contradiction = bool(hypothesis.evidence_against)

    if has_support and not has_contradiction:
        hypothesis.state = EpistemicState.SUPPORTED
    elif has_contradiction and not has_support:
        hypothesis.state = EpistemicState.CONTRADICTED
    else:
        hypothesis.state = EpistemicState.OPEN

    return hypothesis


def apply_rule_result(
    hypothesis: Hypothesis,
    observation: Observation,
    direction: str,
    reason: str,
) -> Hypothesis:
    """Apply a rule result to a hypothesis and update its epistemic state."""

    if direction == "supports":
        add_supporting_evidence(
            hypothesis=hypothesis,
            observation=observation,
            reason=reason,
        )
    elif direction == "contradicts":
        add_contradicting_evidence(
            hypothesis=hypothesis,
            observation=observation,
            reason=reason,
        )

    update_epistemic_state(hypothesis)
    return hypothesis
