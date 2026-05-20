from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List


@dataclass(frozen=True)
class ToolCall:
    name: str
    arguments: Dict[str, object]


@dataclass(frozen=True)
class ToolResult:
    name: str
    output: Dict[str, object]


ToolFunc = Callable[[Dict[str, object]], Dict[str, object]]


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: Dict[str, ToolFunc] = {}

    def register(self, name: str, func: ToolFunc) -> None:
        self._tools[name] = func

    def has(self, name: str) -> bool:
        return name in self._tools

    def run(self, call: ToolCall) -> ToolResult:
        if call.name not in self._tools:
            raise ValueError(f"Tool not registered: {call.name}")
        output = self._tools[call.name](call.arguments)
        return ToolResult(name=call.name, output=output)

    def list_tools(self) -> List[str]:
        return sorted(self._tools.keys())
