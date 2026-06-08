from datetime import datetime
from fastapi import APIRouter
from app.models.schemas import HistoryItem

router = APIRouter(tags=["history"])

@router.get("/", response_model=list[HistoryItem])
def get_history():
    return [
        HistoryItem(
            id="hist-1",
            type="chat",
            summary="Initial research session on industry trends.",
            created_at=datetime.utcnow().isoformat() + "Z",
        )
    ]
