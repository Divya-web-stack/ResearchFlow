from fastapi import APIRouter
from collections import Counter

from app.memory.store import MemoryStore

router = APIRouter(tags=["analytics"])

memory_store = MemoryStore()


@router.get("/")
def analytics():

    memories = memory_store.list_memory()

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