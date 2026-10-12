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

    return _recommend_generic_test(investigation)


def _recommend_generic_test(
    investigation: Investigation,
) -> Experiment | None:
    """Choose the most informative unmeasured variable from evidence rules."""

    candidates = [
        hypothesis
        for hypothesis in investigation.hypotheses
        if hypothesis.state.value != "contradicted"
        and hypothesis.evidence_rules
    ]

    if not candidates:
        return None

    observed_variables = {
        observation.variable
        for observation in investigation.observations
    }

    rules_by_variable: dict[str, dict[str, list]] = {}

    for hypothesis in candidates:
        for rule in hypothesis.evidence_rules:
            if rule.variable in observed_variables:
                continue

            rules_by_variable.setdefault(
                rule.variable,
                {},
            ).setdefault(
                hypothesis.id,
                [],
            ).append(rule)

    if not rules_by_variable:
        return None

    variable, hypothesis_rules = max(
        rules_by_variable.items(),
        key=lambda item: (
            len(item[1]),
            sum(
                len(rules)
                for rules in item[1].values()
            ),
        ),
    )

    hypothesis_lookup = {
        hypothesis.id: hypothesis
        for hypothesis in candidates
    }

    predicted_results: dict[str, str] = {}

    for hypothesis_id, rules in hypothesis_rules.items():
        supporting = [
            rule.reason
            for rule in rules
            if rule.effect.value == "supports"
        ]
        contradicting = [
            rule.reason
            for rule in rules
            if rule.effect.value == "contradicts"
        ]

        parts = []

        if supporting:
            parts.append(
                "Supports: " + " ".join(supporting)
            )

        if contradicting:
            parts.append(
                "Contradicts: " + " ".join(contradicting)
            )

        predicted_results[hypothesis_id] = " ".join(parts)

    units = {
        rule.unit
        for rules in hypothesis_rules.values()
        for rule in rules
        if rule.unit
    }

    unit = next(iter(units), None)

    claims = [
        hypothesis_lookup[hypothesis_id].claim
        for hypothesis_id in hypothesis_rules
    ]

    if len(claims) == 1:
        question = (
            f"What does measuring {variable} tell us about "
            f"{claims[0]}?"
        )
    else:
        question = (
            f"Can measuring {variable} help distinguish between "
            + "; ".join(claims)
            + "?"
        )

    return Experiment(
        question=question,
        target_hypotheses=list(hypothesis_rules),
        observations_required=[
            f"{variable}{f' ({unit})' if unit else ''}"
        ],
        predicted_results=predicted_results,
    )
