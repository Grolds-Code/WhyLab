from whylab.application.builder import InvestigationBuilder
from whylab.domain.models import Experiment, Investigation, Observation
from whylab.reasoning.investigation import apply_observation_to_investigation
from whylab.reasoning.planning import recommend_next_test
from whylab.reasoning.report import EvidenceReport, generate_evidence_report
from whylab.storage.sqlite import InvestigationStore


class WhyLabService:
    """Coordinate persistence and scientific reasoning workflows."""

    def __init__(
        self,
        store: InvestigationStore,
        builder: InvestigationBuilder | None = None,
    ):
        self.store = store
        self.builder = builder

    def create_investigation(
        self,
        investigation: Investigation,
    ) -> Investigation:
        self.store.save(investigation)
        return investigation

    def create_investigation_from_question(
        self,
        question: str,
        investigation_id: str,
    ) -> Investigation:
        if self.builder is None:
            raise RuntimeError(
                "No investigation builder is configured."
            )

        investigation = self.builder.build(
            question=question,
            investigation_id=investigation_id,
        )

        self.store.save(investigation)

        return investigation

    def get_investigation(
        self,
        investigation_id: str,
    ) -> Investigation | None:
        return self.store.get(investigation_id)

    def record_observation(
        self,
        investigation_id: str,
        observation: Observation,
    ) -> Investigation | None:
        investigation = self.store.get(investigation_id)

        if investigation is None:
            return None

        apply_observation_to_investigation(
            investigation,
            observation,
        )

        self.store.save(investigation)

        return investigation

    def get_evidence_report(
        self,
        investigation_id: str,
    ) -> EvidenceReport | None:
        investigation = self.store.get(investigation_id)

        if investigation is None:
            return None

        return generate_evidence_report(investigation)

    def recommend_next_test(
        self,
        investigation_id: str,
    ) -> Experiment | None:
        investigation = self.store.get(investigation_id)

        if investigation is None:
            return None

        return recommend_next_test(investigation)
