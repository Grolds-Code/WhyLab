from pathlib import Path

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

from whylab.application.builder import InvestigationBuilder
from whylab.application.service import WhyLabService
from whylab.domain.models import Experiment, Investigation, Observation
from whylab.interpreters.basil import (
    BasilQuestionInterpreter,
    UnsupportedQuestionError,
)
from whylab.reasoning.report import EvidenceReport
from whylab.storage.sqlite import InvestigationStore


class InvestigationQuestionRequest(BaseModel):
    """Request body for starting an investigation from natural language."""

    investigation_id: str
    question: str


def create_app(
    database_path: str | Path,
    builder: InvestigationBuilder | None = None,
) -> FastAPI:
    """Create the WhyLab HTTP API."""

    store = InvestigationStore(database_path)

    configured_builder = builder or InvestigationBuilder(
        interpreter=BasilQuestionInterpreter(),
    )

    service = WhyLabService(
        store,
        builder=configured_builder,
    )

    app = FastAPI(
        title="WhyLab API",
        version="0.1.0",
        description=(
            "Persistent scientific-reasoning API for hypothesis-driven "
            "real-world investigations."
        ),
    )

    @app.post(
        "/investigations",
        response_model=Investigation,
        status_code=status.HTTP_201_CREATED,
    )
    def create_investigation(
        investigation: Investigation,
    ) -> Investigation:
        return service.create_investigation(investigation)

    @app.post(
        "/investigations/from-question",
        response_model=Investigation,
        status_code=status.HTTP_201_CREATED,
    )
    def create_investigation_from_question(
        request: InvestigationQuestionRequest,
    ) -> Investigation:
        try:
            return service.create_investigation_from_question(
                question=request.question,
                investigation_id=request.investigation_id,
            )
        except UnsupportedQuestionError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=str(exc),
            ) from exc
        except RuntimeError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=str(exc),
            ) from exc

    @app.get(
        "/investigations/{investigation_id}",
        response_model=Investigation,
    )
    def get_investigation(
        investigation_id: str,
    ) -> Investigation:
        investigation = service.get_investigation(investigation_id)

        if investigation is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Investigation not found.",
            )

        return investigation

    @app.post(
        "/investigations/{investigation_id}/observations",
        response_model=Investigation,
    )
    def record_observation(
        investigation_id: str,
        observation: Observation,
    ) -> Investigation:
        investigation = service.record_observation(
            investigation_id,
            observation,
        )

        if investigation is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Investigation not found.",
            )

        return investigation

    @app.get(
        "/investigations/{investigation_id}/report",
        response_model=EvidenceReport,
    )
    def get_evidence_report(
        investigation_id: str,
    ) -> EvidenceReport:
        report = service.get_evidence_report(investigation_id)

        if report is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Investigation not found.",
            )

        return report

    @app.get(
        "/investigations/{investigation_id}/next-test",
        response_model=Experiment,
    )
    def get_next_test(
        investigation_id: str,
    ) -> Experiment:
        experiment = service.recommend_next_test(investigation_id)

        if experiment is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No next test is currently available.",
            )

        return experiment

    return app
