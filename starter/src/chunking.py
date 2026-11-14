"""Implement fixed-size and structure-aware chunking."""
import re
from .models import Chunk, DocumentPage


def fixed_size(page: DocumentPage, size: int = 500, overlap: int = 50) -> list[Chunk]:
    """Split text into overlapping fixed-size windows and retain page metadata."""
    text = page.text
    if not text:
        return []

    chunks: list[Chunk] = []
    step = max(1, size - overlap)
    start = 0
    idx = 1
    total_len = len(text)

    while start < total_len:
        end = min(start + size, total_len)
        chunk_text = text[start:end].strip()
        if chunk_text:
            chunk_id = f"{page.document_id}_p{page.page}_fix_{idx:02d}"
            metadata = dict(page.metadata)
            metadata.update({
                "chunk_id": chunk_id,
                "strategy": "fixed_size",
                "chunk_index": idx,
                "char_length": len(chunk_text)
            })
            chunks.append(
                Chunk(
                    chunk_id=chunk_id,
                    document_id=page.document_id,
                    source=page.source,
                    page=page.page,
                    text=chunk_text,
                    metadata=metadata
                )
            )
            idx += 1
        if end >= total_len:
            break
        start += step

    return chunks


def by_paragraph(page: DocumentPage, max_size: int = 800) -> list[Chunk]:
    """Group paragraphs, split oversized paragraphs and retain metadata."""
    text = page.text
    if not text:
        return []

    # Split by double newlines or clause markers
    raw_paras = [p.strip() for p in text.split("\n\n") if p.strip()]
    if not raw_paras:
        raw_paras = [text]

    chunks: list[Chunk] = []
    current_text = ""
    idx = 1

    def save_chunk(c_text: str):
        nonlocal idx
        c_text = c_text.strip()
        if not c_text:
            return
        chunk_id = f"{page.document_id}_p{page.page}_para_{idx:02d}"
        metadata = dict(page.metadata)
        metadata.update({
            "chunk_id": chunk_id,
            "strategy": "by_paragraph",
            "chunk_index": idx,
            "char_length": len(c_text)
        })
        chunks.append(
            Chunk(
                chunk_id=chunk_id,
                document_id=page.document_id,
                source=page.source,
                page=page.page,
                text=c_text,
                metadata=metadata
            )
        )
        idx += 1

    for para in raw_paras:
        # If single paragraph exceeds max_size, split by sentences
        if len(para) > max_size:
            if current_text:
                save_chunk(current_text)
                current_text = ""
            sentences = re.split(r'(?<=[.!?])\s+', para)
            sub_chunk = ""
            for s in sentences:
                if len(sub_chunk) + len(s) + 1 <= max_size:
                    sub_chunk = (sub_chunk + " " + s).strip()
                else:
                    if sub_chunk:
                        save_chunk(sub_chunk)
                    # If sentence itself is still longer than max_size, hard wrap
                    while len(s) > max_size:
                        save_chunk(s[:max_size])
                        s = s[max_size:]
                    sub_chunk = s
            if sub_chunk:
                save_chunk(sub_chunk)
        else:
            # Check if adding this paragraph exceeds max_size
            if current_text and (len(current_text) + len(para) + 2 > max_size):
                save_chunk(current_text)
                current_text = para
            else:
                if current_text:
                    current_text = current_text + "\n\n" + para
                else:
                    current_text = para

    if current_text:
        save_chunk(current_text)

    return chunks
