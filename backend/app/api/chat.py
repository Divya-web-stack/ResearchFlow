from fastapi import APIRouter
from app.agents.crew_demo import manager_agent
from app.models.schemas import ChatRequest, ChatResponse

router = APIRouter(tags=["chat"])

@router.post("/", response_model=ChatResponse)
def chat(request: ChatRequest):
    result = manager_agent.execute(request.message)
    summary = result.get("write", {}).get("summary", "Manager agent coordinated the research workflow.")
    steps = [f"{step} executed" for step in result.get("steps", [])]
    return ChatResponse(summary=summary, steps=steps, confidence=0.92)
