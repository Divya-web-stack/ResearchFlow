from fastapi import APIRouter
from fastapi.responses import FileResponse

from app.memory.store import MemoryStore
from app.services.pdf_service import generate_pdf

router = APIRouter(tags=["pdf"])

memory_store = MemoryStore()


@router.get("/{memory_id}")
def export_pdf(memory_id: str):

    memories = memory_store.list_memory()

    memory = next(
        (
            item
            for item in memories
            if item["id"] == memory_id
        ),
        None
    )

    if not memory:
        return {
            "error": "Memory not found"
        }

    pdf_path = (
        f"research_report_{memory_id}.pdf"
    )

    generate_pdf(
        title=memory["title"],
        content=memory["content"],
        output_path=pdf_path
    )

    return FileResponse(
        pdf_path,
        filename=pdf_path,
        media_type="application/pdf"
    )