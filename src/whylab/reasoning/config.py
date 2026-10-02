from pydantic import BaseModel


class SoilMoistureRuleConfig(BaseModel):
    """Explicit assumptions used to interpret soil-moisture observations."""

    variable: str = "soil_moisture"
    unit: str = "percent"

    supports_underwatering_at_or_below: float = 30.0
    contradicts_underwatering_at_or_above: float = 60.0

    provenance: str = "WhyLab v0.1 basil demonstration assumption"
    rationale: str = (
        "Initial thresholds used only to demonstrate the reasoning workflow. "
        "They are not asserted as universal botanical thresholds."
    )
