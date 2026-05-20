from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .agent_tools import ToolCall, ToolResult, ToolRegistry


@dataclass(frozen=True)
class AgentStep:
    thought: str
    tool_call: Optional[ToolCall]
    tool_result: Optional[ToolResult]


@dataclass(frozen=True)
class AgentOutput:
    steps: List[AgentStep]
    final: Dict[str, object]


def run_agent(tool_registry: ToolRegistry, plan: List[ToolCall]) -> AgentOutput:
    steps: List[AgentStep] = []
    context: Dict[str, Dict[str, object]] = {}

    for call in plan:
        resolved_args = _resolve_args(call.arguments, context)
        result = tool_registry.run(ToolCall(name=call.name, arguments=resolved_args))
        steps.append(
            AgentStep(
                thought=f"Calling {call.name}",
                tool_call=call,
                tool_result=result,
            )
        )
        context[call.name] = result.output

    final = {
        "tool_results": [step.tool_result.output for step in steps if step.tool_result],
    }

    return AgentOutput(steps=steps, final=final)


def _resolve_args(value: Any, context: Dict[str, Dict[str, object]]) -> Any:
    if isinstance(value, dict):
        if "$ref" in value:
            return context.get(value["$ref"], {})
        return {key: _resolve_args(val, context) for key, val in value.items()}
    if isinstance(value, list):
        return [_resolve_args(item, context) for item in value]
    return value
