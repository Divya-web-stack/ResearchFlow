from __future__ import annotations
from typing import Any, Callable

from app.agents.base import Agent

class ResearchBasedAgent(Agent):
    def __init__(
        self,
        name: str,
        role: str,
        description: str,
        execute: Callable[..., Any] | None = None,
        tools: list[str] | None = None,
    ):
        super().__init__(name=name, role=role, description=description)
        self.tools = tools or []
        self._execute = execute

    def execute(self, *args: Any, **kwargs: Any) -> Any:
        if self._execute is None:
            raise NotImplementedError(f"No execute function defined for agent {self.name}")
        return self._execute(*args, **kwargs)

    def __repr__(self) -> str:
        return f"<ResearchBasedAgent name={self.name!r} role={self.role!r}>"


def create_agent(
    name: str,
    role: str,
    description: str,
    execute: Callable[..., Any] | None = None,
    tools: list[str] | None = None,
) -> ResearchBasedAgent:
    return ResearchBasedAgent(name=name, role=role, description=description, execute=execute, tools=tools)


class AgentRegistry:
    def __init__(self) -> None:
        self._agents: dict[str, Agent] = {}

    def register(self, agent: Agent) -> Agent:
        self._agents[agent.name] = agent
        return agent

    def get(self, name: str) -> Agent | None:
        return self._agents.get(name)

    def list(self) -> list[Agent]:
        return list(self._agents.values())


registry = AgentRegistry()
