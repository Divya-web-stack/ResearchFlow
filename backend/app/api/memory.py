from fastapi import APIRouter, Depends

from app.auth.store import get_current_user
from app.memory.store import MemoryStore

router = APIRouter(tags=["memory"])

memory_store = MemoryStore()


@router.get("/")
def get_memory(
    user: dict = Depends(get_current_user)
):

    memories = memory_store.list_memory_for_user(
        user["id"]
    )

    return memories
