import sqlite3
from collections.abc import Callable
from pathlib import Path

from whylab.domain.models import Investigation


class InvestigationStore:
    """Persist investigations in a local SQLite database."""

    def __init__(
        self,
        database_path: str | Path,
        after_save: Callable[[], None] | None = None,
    ):
        self.database_path = Path(database_path)
        self.after_save = after_save
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.database_path)

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS investigations (
                    id TEXT PRIMARY KEY,
                    payload TEXT NOT NULL
                )
                """
            )

    def save(self, investigation: Investigation) -> None:
        payload = investigation.model_dump_json()

        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO investigations (id, payload)
                VALUES (?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    payload = excluded.payload
                """,
                (investigation.id, payload),
            )

        if self.after_save is not None:
            self.after_save()

    def get(self, investigation_id: str) -> Investigation | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT payload
                FROM investigations
                WHERE id = ?
                """,
                (investigation_id,),
            ).fetchone()

        if row is None:
            return None

        return Investigation.model_validate_json(row[0])
