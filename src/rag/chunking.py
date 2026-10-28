"""
Chunking Strategies for Telecom Support Data.
Implements 3 comparative strategies evaluated against the Golden Benchmark:
1. Strategy A: Fixed-Window Chunking (256 chars, 32 overlap)
2. Strategy B: Field-Aware Structured Chunking (Preserves Domain Context & Circle/Category)
3. Strategy C: Recursive Hierarchical Chunking (512 chars, 64 overlap)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class TextChunk:
    chunk_id: str
    ticket_id: str
    circle: str
    category: str
    text: str
    strategy: str
    metadata: Dict[str, Any]


class BaseChunker(ABC):
    @abstractmethod
    def chunk_ticket(self, ticket: Dict[str, Any]) -> List[TextChunk]:
        """Convert a ticket record into one or more chunks."""
        pass


class FixedWindowChunker(BaseChunker):
    """Strategy A: Baseline fixed character-window chunking."""

    def __init__(self, chunk_size: int = 256, chunk_overlap: int = 32) -> None:
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_ticket(self, ticket: Dict[str, Any]) -> List[TextChunk]:
        ticket_id = ticket.get("ticket_id", "UNKNOWN")
        circle = ticket.get("circle", "NATIONAL")
        category = ticket.get("category", "General")
        raw_text = f"{ticket.get('description_clean', '')} {ticket.get('resolution_notes', '')}".strip()

        if not raw_text:
            return []

        chunks: List[TextChunk] = []
        start = 0
        idx = 0
        step = self.chunk_size - self.chunk_overlap

        while start < len(raw_text):
            chunk_slice = raw_text[start : start + self.chunk_size].strip()
            if chunk_slice:
                chunks.append(
                    TextChunk(
                        chunk_id=f"{ticket_id}_fixed_{idx:02d}",
                        ticket_id=ticket_id,
                        circle=circle,
                        category=category,
                        text=chunk_slice,
                        strategy="fixed_window_256",
                        metadata={
                            "priority": ticket.get("priority", "Medium"),
                            "status": ticket.get("status", "Closed"),
                        },
                    )
                )
                idx += 1
            start += step

        return chunks


class FieldAwareChunker(BaseChunker):
    """
    Strategy B: Telecom Field-Aware Structured Chunking.
    Preserves structural headers (Circle, Category, Priority, Symptom, Resolution).
    Proven in enterprise telecom support to maximize retrieval precision for troubleshooting.
    """

    def chunk_ticket(self, ticket: Dict[str, Any]) -> List[TextChunk]:
        ticket_id = ticket.get("ticket_id", "UNKNOWN")
        circle = ticket.get("circle", "NATIONAL")
        category = ticket.get("category", "General")
        priority = ticket.get("priority", "Medium")
        status = ticket.get("status", "Closed")
        desc = ticket.get("description_clean", "").strip()
        resolution = ticket.get("resolution_notes", "").strip()

        # Build context-rich composite document
        content_lines = [
            f"[TICKET ID]: {ticket_id}",
            f"[REGION/CIRCLE]: {circle}",
            f"[CATEGORY]: {category} | [PRIORITY]: {priority} | [STATUS]: {status}",
            f"[CUSTOMER ISSUE]: {desc}",
        ]
        if resolution:
            content_lines.append(f"[RESOLUTION]: {resolution}")

        structured_text = "\n".join(content_lines)

        return [
            TextChunk(
                chunk_id=f"{ticket_id}_field_00",
                ticket_id=ticket_id,
                circle=circle,
                category=category,
                text=structured_text,
                strategy="field_aware_v1",
                metadata={
                    "priority": priority,
                    "status": status,
                    "created_at": str(ticket.get("created_at", "")),
                },
            )
        ]


class RecursiveChunker(BaseChunker):
    """Strategy C: Recursive character splitting by semantic punctuation boundaries."""

    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 64) -> None:
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = ["\n\n", "\n", ". ", " ", ""]

    def _split_text(self, text: str) -> List[str]:
        if len(text) <= self.chunk_size:
            return [text]

        for sep in self.separators:
            if sep and sep in text:
                parts = text.split(sep)
                result = []
                current = ""
                for part in parts:
                    candidate = f"{current}{sep}{part}" if current else part
                    if len(candidate) <= self.chunk_size:
                        current = candidate
                    else:
                        if current:
                            result.append(current.strip())
                        current = part
                if current:
                    result.append(current.strip())
                return result

        # Fallback to hard slice
        return [text[i : i + self.chunk_size] for i in range(0, len(text), self.chunk_size - self.chunk_overlap)]

    def chunk_ticket(self, ticket: Dict[str, Any]) -> List[TextChunk]:
        ticket_id = ticket.get("ticket_id", "UNKNOWN")
        circle = ticket.get("circle", "NATIONAL")
        category = ticket.get("category", "General")
        combined_text = f"Ticket {ticket_id} ({category}, {circle}): {ticket.get('description_clean', '')} Resolution: {ticket.get('resolution_notes', '')}"

        splits = self._split_text(combined_text)
        chunks = []
        for idx, s in enumerate(splits):
            if s.strip():
                chunks.append(
                    TextChunk(
                        chunk_id=f"{ticket_id}_rec_{idx:02d}",
                        ticket_id=ticket_id,
                        circle=circle,
                        category=category,
                        text=s.strip(),
                        strategy="recursive_512",
                        metadata={"priority": ticket.get("priority", "Medium")},
                    )
                )
        return chunks

