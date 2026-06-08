from pathlib import Path
from typing import Optional

BASE_DIR = Path(__file__).resolve().parents[2]
UPLOAD_DIR = BASE_DIR / "uploads"

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

try:
    import docx
except ImportError:
    docx = None


def extract_text_from_document(document_id: str) -> str:
    candidates = list(UPLOAD_DIR.glob(f"{document_id}_*"))
    if not candidates:
        return "Document not found."

    path = candidates[0]
    suffix = path.suffix.lower()
    if suffix == ".txt":
        return path.read_text(encoding="utf-8", errors="ignore")
    if suffix == ".pdf" and pdfplumber is not None:
        with pdfplumber.open(path) as pdf:
            return "\n\n".join(page.extract_text() or "" for page in pdf.pages)
    if suffix in {".docx", ".doc"} and docx is not None:
        document = docx.Document(path)
        return "\n".join(p.text for p in document.paragraphs)
    return "Document format is unsupported or required parser is not installed."
