from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.chat import router as chat_router
from app.api.research import router as research_router
from app.api.upload import router as upload_router
from app.api.document import router as document_router
from app.api.memory import router as memory_router
from app.api.report import router as report_router
from app.api.history import router as history_router
from app.api.agents import router as agents_router
from app.api.pdf import router as pdf_router
from app.api.analytics import router as analytics_router
from app.api.auth import router as auth_router

app = FastAPI(
    title="AgentFlow AI",
    description="Multi-Agent Research & Knowledge Generation API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix="/api/chat")
app.include_router(auth_router, prefix="/api/auth")
app.include_router(research_router, prefix="/api/research")
app.include_router(upload_router, prefix="/api/upload")
app.include_router(document_router, prefix="/api/document")
app.include_router(memory_router, prefix="/api/memory")
app.include_router(report_router, prefix="/api/report")
app.include_router(history_router, prefix="/api/history")
app.include_router(agents_router, prefix="/api/agents")
app.include_router(
    pdf_router,
    prefix="/api/pdf"
)
app.include_router(
    analytics_router,
    prefix="/api/analytics"
)
