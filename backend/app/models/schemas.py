from typing import Any, List, Optional
from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str


class AgentWorkflowRequest(BaseModel):
    query: str
    limit: Optional[int] = 4


class AgentWorkflowResponse(BaseModel):
    query: str
    summary: str
    steps: List[str]
    results: Any

class ChatResponse(BaseModel):
    summary: str
    steps: List[str]
    confidence: float

class ResearchRequest(BaseModel):
    query: str
    limit: int = 5
    chat_history: List[dict[str, Any]] = []

class ResearchSource(BaseModel):
    title: str
    url: str
    snippet: str

class ResearchResponse(BaseModel):
    query: str
    sources: List[ResearchSource]
    highlights: List[str]

class UploadResponse(BaseModel):
    upload_id: str
    filename: str
    message: str

class DocumentQueryRequest(BaseModel):
    document_id: str
    question: str

class DocumentQueryResponse(BaseModel):
    document_id: str
    question: str
    answer: str
    citations: List[str]

class MemoryItem(BaseModel):
    id: str
    title: str
    content: str
    tags: List[str]

class ReportRequest(BaseModel):
    title: str
    prompt: str
    format: Optional[str] = "summary"

class ReportResponse(BaseModel):
    report_id: str
    status: str
    preview: str

class HistoryItem(BaseModel):
    id: str
    type: str
    summary: str
    created_at: str
