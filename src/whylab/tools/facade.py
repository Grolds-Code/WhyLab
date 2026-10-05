from whylab.application.service import WhyLabService
from whylab.domain.models import Experiment, Investigation, Observation
from whylab.reasoning.report import EvidenceReport


class WhyLabTools:
    """Tool-facing façade for WhyLab investigation workflows."""

    def __init__(self, service: WhyLabService):
        self.service = service

    def start_investigation(
        self,
        investigation_id: str,
        question: str,
    ) -> Investigation:
        return self.service.create_investigation_from_question(
            question=question,
            investigation_id=investigation_id,
        )

    def record_observation(
        self,
        investigation_id: str,
        variable: str,
        value: str | int | float | bool,
        unit: str | None = None,
        source: str = "user_report",
        notes: str | None = None,
    ) -> Investigation | None:
        observation = Observation(
            variable=variable,
            value=value,
            unit=unit,
            source=source,
            notes=notes,
        )

        return self.service.record_observation(
            investigation_id,
            observation,
        )

    def get_evidence_report(
        self,
        investigation_id: str,
    ) -> EvidenceReport | None:
        return self.service.get_evidence_report(
            investigation_id,
        )

    def get_next_test(
        self,
        investigation_id: str,
    ) -> Experiment | None:
        return self.service.recommend_next_test(
            investigation_id,
        )
