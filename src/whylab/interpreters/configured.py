import os

from whylab.application.builder import QuestionInterpreter
from whylab.interpreters.basil import BasilQuestionInterpreter
from whylab.interpreters.llm import LLMQuestionInterpreter


def create_default_interpreter() -> QuestionInterpreter:
    """Create the configured question interpreter for the current environment."""

    api_key = os.getenv("WHYLAB_LLM_API_KEY")

    if not api_key:
        return BasilQuestionInterpreter()

    return LLMQuestionInterpreter(
        api_key=api_key,
        model=os.getenv(
            "WHYLAB_LLM_MODEL",
            "openrouter/free",
        ),
        base_url=os.getenv(
            "WHYLAB_LLM_BASE_URL",
            "https://openrouter.ai/api/v1",
        ),
    )
