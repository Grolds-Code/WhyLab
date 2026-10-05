from whylab.application.builder import (
    HypothesisDraft,
    InvestigationDraft,
)


class UnsupportedQuestionError(ValueError):
    """Raised when the deterministic MVP interpreter cannot handle a question."""


class BasilQuestionInterpreter:
    """Interpret the supported WhyLab v0.1 basil-wilting scenario."""

    def interpret(self, question: str) -> InvestigationDraft:
        normalized = question.lower()

        if "basil" not in normalized or "wilt" not in normalized:
            raise UnsupportedQuestionError(
                "WhyLab v0.1 currently supports basil-wilting investigations only."
            )

        return InvestigationDraft(
            domain="gardening",
            variables=[
                "soil_moisture",
                "drainage",
                "light_exposure",
            ],
            confounders=[
                "temperature",
                "recent_repottings",
                "root_damage",
            ],
            hypotheses=[
                HypothesisDraft(
                    claim="The plant is underwatered",
                    predictions=[
                        "Soil moisture should be relatively low.",
                        "Wilting should improve after adequate watering.",
                    ],
                    falsifiers=[
                        (
                            "Soil remains persistently moist while wilting "
                            "continues."
                        ),
                    ],
                    confounders=[
                        "high_temperature",
                    ],
                ),
                HypothesisDraft(
                    claim="Excess water is causing root stress",
                    predictions=[
                        "Soil should remain persistently wet.",
                        (
                            "Wilting should improve if drainage improves and "
                            "the root zone becomes less saturated."
                        ),
                    ],
                    falsifiers=[
                        (
                            "The root zone dries normally while wilting "
                            "continues."
                        ),
                    ],
                    confounders=[
                        "root_damage",
                        "recent_repottings",
                    ],
                ),
                HypothesisDraft(
                    claim="The plant is receiving insufficient light",
                    predictions=[
                        (
                            "The plant should receive relatively little useful "
                            "light exposure."
                        ),
                        (
                            "Improving light exposure should improve the plant's "
                            "condition if light is the main cause."
                        ),
                    ],
                    falsifiers=[
                        (
                            "Adequate light exposure does not improve the "
                            "condition while other factors remain stable."
                        ),
                    ],
                    confounders=[
                        "temperature",
                    ],
                ),
            ],
        )
