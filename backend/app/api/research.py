import json

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.auth.store import get_current_user
from app.models.schemas import ResearchRequest
from app.agents.crew_demo import manager_agent, manager_execute_stream

router = APIRouter(tags=["research"])


@router.post("/")
def research(
    request: ResearchRequest,
    user: dict = Depends(get_current_user)
):

    print("CHAT HISTORY =", request.chat_history)

    return manager_agent.execute(
    query=request.query,
    limit=request.limit,
    chat_history=request.chat_history,
    user_id=user["id"]
)


@router.post("/stream")
def research_stream(
    request: ResearchRequest,
    user: dict = Depends(get_current_user)
):

    def event_stream():

        try:

            for event in manager_execute_stream(
                query=request.query,
                limit=request.limit,
                chat_history=request.chat_history,
                user_id=user["id"]
            ):

                yield (
                    f"data: {json.dumps(event)}\n\n"
                )

        except Exception as exc:

            yield (
                "data: "
                + json.dumps(
                    {
                        "type": "error",
                        "message": str(exc)
                    }
                )
                + "\n\n"
            )

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream"
    )
