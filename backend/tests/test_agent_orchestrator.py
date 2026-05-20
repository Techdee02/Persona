from backend.agent_orchestrator import run_agent
from backend.agent_tools import ToolCall, ToolRegistry


def test_agent_orchestrator_runs_plan():
    registry = ToolRegistry()
    registry.register("echo", lambda args: {"value": args["value"]})

    plan = [ToolCall(name="echo", arguments={"value": "ok"})]
    output = run_agent(registry, plan)

    assert len(output.steps) == 1
    assert output.final["tool_results"][0]["value"] == "ok"
