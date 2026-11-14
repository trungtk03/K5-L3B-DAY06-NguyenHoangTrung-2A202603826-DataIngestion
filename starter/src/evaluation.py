"""Evaluate retrieved evidence and preserve per-query traces."""
from typing import Any
import unicodedata


def _normalize_for_match(text: str) -> str:
    """Normalize text for evidence comparison."""
    if not text:
        return ""
    norm = unicodedata.normalize("NFC", text).lower()
    return " ".join(norm.split())


def is_chunk_hit(gold_source_id: str, gold_page: int, evidence_quote: str, chunk: dict[str, Any]) -> tuple[bool, str]:
    """Check if a retrieved chunk satisfies the hit condition:

    1. Same source document.
    2. Same page (or documented alternative).
    3. Contains the core evidence quote or substantial key evidence text.
    """
    meta = chunk.get("metadata", {})
    chunk_doc = str(meta.get("document_id", "")).strip()
    chunk_page = meta.get("page", None)
    chunk_text = _normalize_for_match(chunk.get("text", ""))

    gold_doc = str(gold_source_id).strip()
    norm_evidence = _normalize_for_match(evidence_quote)

    # Check document and page match
    doc_match = (chunk_doc == gold_doc)
    page_match = False
    try:
        page_match = (int(chunk_page) == int(gold_page))
    except (TypeError, ValueError):
        page_match = False

    if not doc_match:
        return False, f"Document mismatch: got '{chunk_doc}', expected '{gold_doc}'"

    if not page_match:
        return False, f"Page mismatch: got p{chunk_page}, expected p{gold_page}"

    # Check evidence containment:
    # Full substring match or sentence segments match
    if norm_evidence in chunk_text:
        return True, "Full evidence quote found in chunk text."

    # If evidence was slightly split or whitespace varies, check key phrases
    evidence_words = norm_evidence.split()
    if len(evidence_words) > 6:
        # Check if first 5 words and last 5 words are present
        head = " ".join(evidence_words[:5])
        tail = " ".join(evidence_words[-5:])
        if head in chunk_text or tail in chunk_text:
            return True, "Core evidence segment found in chunk text."

    return False, "Evidence quote not found in chunk text."


def evaluate_query(question: dict[str, Any], hits: list[dict[str, Any]]) -> dict[str, Any]:
    """Check source/page and gold evidence; keep hit@1 and hit@3 trace."""
    gold_doc = question.get("gold_source_id", "handbook_2024")
    gold_page = question.get("gold_page", 0)
    evidence_quote = question.get("evidence_quote", "")

    hit_top1 = False
    hit_top3 = False
    evaluated_hits = []

    for rank, h in enumerate(hits[:3], start=1):
        is_hit, reason = is_chunk_hit(gold_doc, gold_page, evidence_quote, h)
        evaluated_chunk = {
            "rank": rank,
            "chunk_id": h.get("chunk_id", ""),
            "score": h.get("score", 0.0),
            "page": h.get("metadata", {}).get("page", None),
            "category": h.get("metadata", {}).get("category", ""),
            "section": h.get("metadata", {}).get("section", ""),
            "text": h.get("text", ""),
            "is_hit": is_hit,
            "reason": reason
        }
        evaluated_hits.append(evaluated_chunk)
        if is_hit:
            if rank == 1:
                hit_top1 = True
            hit_top3 = True

    return {
        "question_id": question.get("id", ""),
        "split": question.get("split", "dev"),
        "type": question.get("type", "truc_tiep"),
        "question": question.get("question", ""),
        "expected_answer": question.get("expected_answer", ""),
        "gold_source_id": gold_doc,
        "gold_page": gold_page,
        "evidence_quote": evidence_quote,
        "filter": question.get("filter", None),
        "hit_top1": hit_top1,
        "hit_top3": hit_top3,
        "top3_chunks": evaluated_hits
    }


def summarize(traces: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate Hit@1 and Evidence Hit@3 by split (dev / test)."""
    splits = {"dev": [], "test": [], "all": traces}
    for t in traces:
        s = t.get("split", "dev")
        if s in splits:
            splits[s].append(t)

    summary: dict[str, Any] = {}
    for s_name, s_traces in splits.items():
        total = len(s_traces)
        if total == 0:
            summary[s_name] = {
                "total": 0,
                "hit1_count": 0,
                "hit1_ratio": 0.0,
                "hit1_str": "0/0",
                "hit3_count": 0,
                "hit3_ratio": 0.0,
                "hit3_str": "0/0"
            }
            continue

        hit1_count = sum(1 for t in s_traces if t.get("hit_top1", False))
        hit3_count = sum(1 for t in s_traces if t.get("hit_top3", False))

        summary[s_name] = {
            "total": total,
            "hit1_count": hit1_count,
            "hit1_ratio": round(hit1_count / total, 4),
            "hit1_str": f"{hit1_count}/{total}",
            "hit3_count": hit3_count,
            "hit3_ratio": round(hit3_count / total, 4),
            "hit3_str": f"{hit3_count}/{total}"
        }
    return summary
