from fastapi import APIRouter

from app.memory.store import MemoryStore

router = APIRouter(tags=["memory"])

memory_store = MemoryStore()


@router.get("/")
def get_memory():

    memories = memory_store.list_memory()

    return memories