from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

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

    for call in plan:
        result = tool_registry.run(call)
        steps.append(
            AgentStep(
                thought=f"Calling {call.name}",
                tool_call=call,
                tool_result=result,
            )
        )

    final = {
        "tool_results": [step.tool_result.output for step in steps if step.tool_result],
    }

    return AgentOutput(steps=steps, final=final)
