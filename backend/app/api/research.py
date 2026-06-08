from fastapi import APIRouter

from app.models.schemas import ResearchRequest
from app.agents.crew_demo import manager_agent

router = APIRouter(tags=["research"])


@router.post("/")
def research(request: ResearchRequest):

    print("CHAT HISTORY =", request.chat_history)

    return manager_agent.execute(
    query=request.query,
    limit=request.limit,
    chat_history=request.chat_history
)