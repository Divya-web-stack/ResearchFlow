from __future__ import annotations
from typing import Any
from app.agents.base import Agent

class ResearchBasedAgent:
    def __init__(self, name: str, agents: list[Agent] | None = None) -> None:
        self.name = name
        self.agents = agents or []

    def add(self, agent: Agent) -> None:
        self.agents.append(agent)

    def execute(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        results = {}
        for agent in self.agents:
            try:
                results[agent.name] = agent.execute(*args, **kwargs)
            except Exception as exc:
                results[agent.name] = {"error": str(exc)}
        return results

    def __repr__(self) -> str:
        return f"<ResearchBasedAgent name={self.name!r} agents={[agent.name for agent in self.agents]}>"
