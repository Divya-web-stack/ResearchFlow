from __future__ import annotations
from typing import Any

class Agent:
    def __init__(
        self,
        role: str,
        name: str | None = None,
        description: str = "",
        goal: str | None = None,
        verbose: bool = False,
        memory: bool = False,
        backstory: str | None = None,
        tools: list[Any] | None = None,
        allow_delegation: bool = False,
        llm: Any | None = None,
    ):
        self.name = name or role
        self.role = role
        self.description = description
        self.goal = goal
        self.verbose = verbose
        self.memory = memory
        self.backstory = backstory
        self.tools = tools or []
        self.allow_delegation = allow_delegation
        self.llm = llm

    def execute(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError("Agent subclasses must implement execute().")

    def __repr__(self) -> str:
        return (
            f"<Agent name={self.name!r} role={self.role!r} goal={self.goal!r} "
            f"verbose={self.verbose} memory={self.memory} tools={self.tools} "
            f"allow_delegation={self.allow_delegation} llm={bool(self.llm)}>"
        )
