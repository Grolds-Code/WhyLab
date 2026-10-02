from pydantic import BaseModel, Field

from whylab.domain.models import Investigation


class HypothesisSummary(BaseModel):
    """Judge-friendly summary of one hypothesis."""

    id: str
    claim: str
    state: str
    evidence_for: list[str] = Field(default_factory=list)
    evidence_against: list[str] = Field(default_factory=list)
    uncertainties: list[str] = Field(default_factory=list)


class EvidenceReport(BaseModel):
    """Structured summary of what an investigation has learned so far."""

    investigation_id: str
    question: str
    supported: list[HypothesisSummary] = Field(default_factory=list)
    contradicted: list[HypothesisSummary] = Field(default_factory=list)
    open: list[HypothesisSummary] = Field(default_factory=list)
    observation_count: int = 0


def generate_evidence_report(
    investigation: Investigation,
) -> EvidenceReport:
    """Generate a structured report from the current investigation state."""

    report = EvidenceReport(
        investigation_id=investigation.id,
        question=investigation.question,
        observation_count=len(investigation.observations),
    )

    for hypothesis in investigation.hypotheses:
        summary = HypothesisSummary(
            id=hypothesis.id,
            claim=hypothesis.claim,
            state=hypothesis.state.value,
            evidence_for=hypothesis.evidence_for,
            evidence_against=hypothesis.evidence_against,
            uncertainties=hypothesis.uncertainties,
        )

        if hypothesis.state.value == "supported":
            report.supported.append(summary)
        elif hypothesis.state.value == "contradicted":
            report.contradicted.append(summary)
        else:
            report.open.append(summary)

    return report
