from fastapi import APIRouter

from app.agents.agent import registry
from app.agents.crew_demo import manager_agent

from app.models.schemas import (
    AgentWorkflowRequest,
    AgentWorkflowResponse
)

router = APIRouter(tags=["agents"])


@router.get("/")
def get_agents():

    return [
        {
            "name": agent.name,
            "role": agent.role,
            "description": agent.description,
            "tools": getattr(agent, "tools", [])
        }
        for agent in registry.list()
    ]


@router.post(
    "/execute",
    response_model=AgentWorkflowResponse
)
def execute_agent_workflow(
    request: AgentWorkflowRequest
):

    result = manager_agent.execute(
        request.query,
        limit=request.limit
    )

    summary = (
        result.get("report", {})
        .get("executive_summary",
             "Agent workflow completed.")
    )

    steps = [
        f"{step} executed"
        for step in result.get(
            "workflow",
            []
        )
    ]

    return AgentWorkflowResponse(
        query=request.query,
        summary=summary,
        steps=steps,
        results=result,
    )