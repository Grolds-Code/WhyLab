from whylab.interpreters.basil import BasilQuestionInterpreter
from whylab.interpreters.configured import create_default_interpreter
from whylab.interpreters.llm import LLMQuestionInterpreter


def test_default_interpreter_falls_back_to_basil_without_key(monkeypatch):
    monkeypatch.delenv("WHYLAB_LLM_API_KEY", raising=False)

    interpreter = create_default_interpreter()

    assert isinstance(interpreter, BasilQuestionInterpreter)


def test_default_interpreter_uses_llm_when_key_is_configured(monkeypatch):
    monkeypatch.setenv("WHYLAB_LLM_API_KEY", "test-key")
    monkeypatch.setenv("WHYLAB_LLM_MODEL", "test-model")
    monkeypatch.setenv("WHYLAB_LLM_BASE_URL", "https://example.test/v1")

    interpreter = create_default_interpreter()

    assert isinstance(interpreter, LLMQuestionInterpreter)
    assert interpreter.api_key == "test-key"
    assert interpreter.model == "test-model"
    assert interpreter.base_url == "https://example.test/v1"
