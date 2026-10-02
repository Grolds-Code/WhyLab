from whylab.domain.models import Hypothesis, Observation


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
