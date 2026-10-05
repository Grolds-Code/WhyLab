from whylab.application.builder import InvestigationBuilder
from whylab.application.service import WhyLabService
from whylab.interpreters.basil import BasilQuestionInterpreter
from whylab.storage.sqlite import InvestigationStore
from whylab.tools.facade import WhyLabTools


def test_tools_expose_complete_investigation_workflow(tmp_path):
    store = InvestigationStore(tmp_path / "whylab.db")
    builder = InvestigationBuilder(
        interpreter=BasilQuestionInterpreter(),
    )
    service = WhyLabService(
        store,
        builder=builder,
    )
    tools = WhyLabTools(service)

    investigation = tools.start_investigation(
        investigation_id="INV-TOOLS-001",
        question=(
            "My basil keeps wilting even though I'm watering it. "
            "Help me figure out why."
        ),
    )

    assert investigation.id == "INV-TOOLS-001"
    assert len(investigation.hypotheses) == 3

    updated = tools.record_observation(
        investigation_id="INV-TOOLS-001",
        variable="soil_moisture",
        value=67,
        unit="percent",
    )

    assert updated is not None
    assert updated.hypotheses[0].state.value == "contradicted"
    assert updated.hypotheses[1].state.value == "supported"

    report = tools.get_evidence_report("INV-TOOLS-001")

    assert report is not None
    assert len(report.supported) == 1
    assert len(report.contradicted) == 1

    next_test = tools.get_next_test("INV-TOOLS-001")

    assert next_test is not None
    assert next_test.variable_changed == "drainage"
