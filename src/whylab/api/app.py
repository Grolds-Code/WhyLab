from pathlib import Path

from fastapi import FastAPI, HTTPException, status

from whylab.application.service import WhyLabService
from whylab.domain.models import Investigation, Observation
from whylab.storage.sqlite import InvestigationStore


def create_app(database_path: str | Path) -> FastAPI:
    """Create the WhyLab HTTP API."""

    store = InvestigationStore(database_path)
    service = WhyLabService(store)

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

    return app
