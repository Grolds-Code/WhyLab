from typing import Protocol

from pydantic import BaseModel, Field

from whylab.domain.models import Hypothesis, Investigation


class HypothesisDraft(BaseModel):
    """A proposed explanation produced during question interpretation."""

    claim: str
    predictions: list[str] = Field(default_factory=list)
    falsifiers: list[str] = Field(default_factory=list)
    confounders: list[str] = Field(default_factory=list)
    uncertainties: list[str] = Field(default_factory=list)


class InvestigationDraft(BaseModel):
    """Structured interpretation of a user's natural-language question."""

    domain: str
    hypotheses: list[HypothesisDraft] = Field(default_factory=list)
    variables: list[str] = Field(default_factory=list)
    confounders: list[str] = Field(default_factory=list)


class QuestionInterpreter(Protocol):
    """Boundary for components that interpret natural-language questions."""

    def interpret(self, question: str) -> InvestigationDraft:
        ...


class InvestigationBuilder:
    """Convert an interpreted question into WhyLab's canonical domain model."""

    def __init__(self, interpreter: QuestionInterpreter):
        self.interpreter = interpreter

    def build(
        self,
        question: str,
        investigation_id: str,
    ) -> Investigation:
        draft = self.interpreter.interpret(question)

        hypotheses = [
            Hypothesis(
                id=f"H{index}",
                claim=hypothesis.claim,
                predictions=hypothesis.predictions,
                falsifiers=hypothesis.falsifiers,
                confounders=hypothesis.confounders,
                uncertainties=hypothesis.uncertainties,
            )
            for index, hypothesis in enumerate(
                draft.hypotheses,
                start=1,
            )
        ]

        return Investigation(
            id=investigation_id,
            question=question,
            domain=draft.domain,
            hypotheses=hypotheses,
            variables=draft.variables,
            confounders=draft.confounders,
        )
