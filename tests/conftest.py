import pytest


@pytest.fixture(autouse=True)
def isolate_llm_environment(monkeypatch):
    """Prevent ordinary tests from accidentally calling external LLM services."""

    monkeypatch.delenv("WHYLAB_LLM_API_KEY", raising=False)
    monkeypatch.delenv("WHYLAB_LLM_MODEL", raising=False)
    monkeypatch.delenv("WHYLAB_LLM_BASE_URL", raising=False)
