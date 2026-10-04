from whylab.domain.models import Experiment, Investigation


def recommend_next_test(
    investigation: Investigation,
) -> Experiment | None:
    """Recommend the next discriminating test for the basil investigation."""

    hypotheses = {
        hypothesis.id: hypothesis
        for hypothesis in investigation.hypotheses
    }

    root_stress = hypotheses.get("H2")
    insufficient_light = hypotheses.get("H3")

    if (
        root_stress is not None
        and insufficient_light is not None
        and root_stress.state.value == "supported"
        and insufficient_light.state.value == "open"
    ):
        return Experiment(
            question=(
                "Does improving drainage reduce wilting while light exposure "
                "and watering are kept stable?"
            ),
            target_hypotheses=["H2", "H3"],
            variable_changed="drainage",
            variables_held_constant=[
                "watering amount",
                "light exposure",
            ],
            observations_required=[
                "soil moisture",
                "wilting severity",
                "drainage behavior",
            ],
            duration_days=3,
            predicted_results={
                "H2": (
                    "If root stress from excess water is contributing, "
                    "improved drainage should reduce wilting as the root zone "
                    "becomes less persistently wet."
                ),
                "H3": (
                    "If insufficient light is the main cause, improving drainage "
                    "alone should not substantially reduce wilting."
                ),
            },
        )

    return None
