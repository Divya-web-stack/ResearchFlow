from fastapi import APIRouter
from fastapi import Depends
from collections import Counter

from app.auth.store import get_current_user
from app.memory.store import MemoryStore

router = APIRouter(tags=["analytics"])

memory_store = MemoryStore()


@router.get("/")
def analytics(
    user: dict = Depends(get_current_user)
):

    memories = memory_store.list_memory_for_user(
        user["id"]
    )

    total_queries = len(memories)

    topics = []

    for memory in memories:

        title = memory.get("title", "")

        topic = (
            title
            .replace("Research memory for:", "")
            .strip()
        )

        topics.append(topic)

    top_topics = Counter(topics).most_common(5)

    return {
        "total_queries": total_queries,
        "total_reports": total_queries,
        "top_topics": top_topics
    }
