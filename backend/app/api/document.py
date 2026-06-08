from fastapi import APIRouter
from app.models.schemas import DocumentQueryRequest, DocumentQueryResponse
from app.services.document_parser import extract_text_from_document

router = APIRouter(tags=["document"])

@router.post("/query", response_model=DocumentQueryResponse)
def query_document(request: DocumentQueryRequest):
    text = extract_text_from_document(request.document_id)
    answer = "This is a placeholder response for the document query."
    citations = ["Document source", "Verifier summary"]
    return DocumentQueryResponse(
        document_id=request.document_id,
        question=request.question,
        answer=answer,
        citations=citations,
    )
