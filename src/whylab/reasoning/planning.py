from whylab.domain.models import Experiment, Investigation


def recommend_next_test(
    investigation: Investigation,
) -> Experiment | None:
    """Recommend the next discriminating test for the basil investigation."""

    hypothesis_ids = {hypothesis.id for hypothesis in investigation.hypotheses}

    if {"H2", "H3"}.issubset(hypothesis_ids):
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
