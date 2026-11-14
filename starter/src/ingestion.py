"""Read and normalize source data."""
import json
from pathlib import Path
import unicodedata
from typing import Any
from .models import DocumentPage


def normalize_text(text: str) -> str:
    """Normalize Unicode (NFC) and whitespace without discarding useful structure."""
    if not text:
        return ""
    # NFC normalization for Vietnamese diacritics
    normalized = unicodedata.normalize("NFC", text)
    # Replace carriage returns and excessive horizontal whitespace
    lines = [line.strip() for line in normalized.splitlines()]
    # Preserve paragraph breaks (double newline)
    paragraphs: list[str] = []
    current_para: list[str] = []
    for line in lines:
        if not line:
            if current_para:
                paragraphs.append(" ".join(current_para))
                current_para = []
        else:
            current_para.append(line)
    if current_para:
        paragraphs.append(" ".join(current_para))
    return "\n\n".join(paragraphs)


def load_corpus_json(path: Path) -> list[DocumentPage]:
    """Load pages from structured JSON corpus and normalize text."""
    if not path.exists():
        raise FileNotFoundError(f"Corpus file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    pages: list[DocumentPage] = []
    for item in data:
        norm_text = normalize_text(item.get("text", ""))
        metadata: dict[str, Any] = {
            "section": item.get("section", ""),
            "category": item.get("category", ""),
            "audience": item.get("audience", ""),
            "title": item.get("title", ""),
            "year": item.get("year", 2024),
            "char_count": len(norm_text)
        }
        page = DocumentPage(
            document_id=item.get("document_id", "handbook_2024"),
            source=item.get("source", str(path)),
            page=int(item.get("page", len(pages) + 1)),
            text=norm_text,
            metadata=metadata
        )
        pages.append(page)
    return pages


def load_pdf(path: Path, document_id: str, source: str) -> list[DocumentPage]:
    """Extract each physical page; keep its page number and source."""
    if not path.exists():
        raise FileNotFoundError(f"PDF file not found: {path}")
    try:
        from pypdf import PdfReader
    except ImportError:
        raise ImportError("pypdf is required to load PDF documents.")

    reader = PdfReader(str(path))
    pages: list[DocumentPage] = []
    for idx, page in enumerate(reader.pages, start=1):
        raw_text = page.extract_text() or ""
        norm_text = normalize_text(raw_text)
        pages.append(
            DocumentPage(
                document_id=document_id,
                source=source,
                page=idx,
                text=norm_text,
                metadata={"page": idx, "char_count": len(norm_text)}
            )
        )
    return pages
