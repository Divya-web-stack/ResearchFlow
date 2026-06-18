from fastapi import APIRouter, Depends
from app.auth.store import get_current_user
from app.agents.crew_demo import manager_agent
from app.models.schemas import ChatRequest, ChatResponse

router = APIRouter(tags=["chat"])

@router.post("/", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    user: dict = Depends(get_current_user)
):
    result = manager_agent.execute(
        request.message,
        user_id=user["id"]
    )
    summary = (
        result.get("report", {})
        .get("executive_summary",
             "Manager agent coordinated the research workflow.")
    )
    steps = [
        f"{step} executed"
        for step in result.get("workflow", [])
    ]
    return ChatResponse(summary=summary, steps=steps, confidence=0.92)







