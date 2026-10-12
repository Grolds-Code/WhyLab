from datetime import datetime, timezone
from enum import StrEnum

from pydantic import BaseModel, Field, model_validator


class EpistemicState(StrEnum):
    """How strongly the current evidence supports a claim."""

    OPEN = "open"
    SUPPORTED = "supported"
    KNOWN = "known"
    CONTRADICTED = "contradicted"


class ComparisonOperator(StrEnum):
    """Deterministic comparison used by an evidence rule."""

    LT = "<"
    LTE = "<="
    GT = ">"
    GTE = ">="
    EQ = "=="
    NEQ = "!="


class EvidenceEffect(StrEnum):
    """How a satisfied evidence rule affects a hypothesis."""

    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"


class EvidenceRule(BaseModel):
    """Machine-readable criterion connecting an observation to a hypothesis."""

    variable: str
    operator: ComparisonOperator
    value: str | int | float | bool
    unit: str | None = None
    effect: EvidenceEffect
    reason: str
    provenance: str = "investigation_assumption"
    rationale: str | None = None

    @model_validator(mode="after")
    def validate_comparison_value(self):
        ordered = {
            ComparisonOperator.LT,
            ComparisonOperator.LTE,
            ComparisonOperator.GT,
            ComparisonOperator.GTE,
        }

        if self.operator in ordered:
            if (
                isinstance(self.value, bool)
                or not isinstance(self.value, (int, float))
            ):
                raise ValueError(
                    "Ordered evidence-rule comparisons require a numeric value."
                )

        return self


class Hypothesis(BaseModel):
    """A falsifiable candidate explanation within an investigation."""

    id: str
    claim: str
    state: EpistemicState = EpistemicState.OPEN

    predictions: list[str] = Field(default_factory=list)
    evidence_for: list[str] = Field(default_factory=list)
    evidence_against: list[str] = Field(default_factory=list)
    falsifiers: list[str] = Field(default_factory=list)
    confounders: list[str] = Field(default_factory=list)
    uncertainties: list[str] = Field(default_factory=list)
    evidence_rules: list[EvidenceRule] = Field(default_factory=list)


class Observation(BaseModel):
    """A real-world observation reported or measured during an investigation."""

    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    variable: str
    value: str | int | float | bool
    unit: str | None = None
    source: str = "user_report"
    notes: str | None = None


class Experiment(BaseModel):
    """A planned observation or intervention used to distinguish hypotheses."""

    question: str
    target_hypotheses: list[str] = Field(default_factory=list)
    variable_changed: str | None = None
    variables_held_constant: list[str] = Field(default_factory=list)
    observations_required: list[str] = Field(default_factory=list)
    duration_days: int | None = None
    predicted_results: dict[str, str] = Field(default_factory=dict)


class Investigation(BaseModel):
    """A persistent scientific investigation spanning one or more sessions."""

    id: str
    question: str
    domain: str
    status: str = "open"

    hypotheses: list[Hypothesis] = Field(default_factory=list)
    observations: list[Observation] = Field(default_factory=list)
    variables: list[str] = Field(default_factory=list)
    confounders: list[str] = Field(default_factory=list)
    experiments: list[Experiment] = Field(default_factory=list)

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
