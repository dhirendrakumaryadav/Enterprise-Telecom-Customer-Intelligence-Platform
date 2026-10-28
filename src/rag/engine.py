"""
End-to-End RAG Engine for Telecom Customer Intelligence.
Orchestrates: Query Embedding -> RBAC Metadata Filtering -> Qdrant Retrieval -> Prompt Construction -> Ollama Generation.
"""

from __future__ import annotations

import time
import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .embeddings import EmbeddingService
from .llm_client import BaseLLMClient, OllamaClient
from .vector_store import QdrantVectorStore

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an enterprise telecom operational AI assistant.
Answer the user's inquiry strictly using the provided context from internal support tickets.
Rules:
1. Always cite the relevant [TICKET ID] you used to find the answer.
2. If the context does not contain sufficient details to answer, state: "Insufficient internal ticket data to resolve this query."
3. Never disclose masked personal identifiers or speculate on unverified causes."""


@dataclass
class RAGResponse:
    query: str
    answer: str
    retrieved_chunks: List[Dict[str, Any]]
    cited_tickets: List[str]
    retrieval_time_ms: float
    generation_time_ms: float
    total_time_ms: float


class TelecomRAGEngine:
    def __init__(
        self,
        vector_store: QdrantVectorStore,
        embedding_service: EmbeddingService,
        llm_client: Optional[BaseLLMClient] = None,
    ) -> None:
        self.vector_store = vector_store
        self.embedding_service = embedding_service
        self.llm_client = llm_client or OllamaClient()

    def query(
        self,
        question: str,
        circle: Optional[str] = None,
        category: Optional[str] = None,
        top_k: int = 3,
    ) -> RAGResponse:
        t0 = time.perf_counter()

        # Step 1: Embed query
        q_vec = self.embedding_service.embed_query(question)

        # Step 2: Retrieve with metadata access filters
        t_ret_start = time.perf_counter()
        retrieved = self.vector_store.search(
            query_vector=q_vec,
            top_k=top_k,
            circle=circle,
            category=category,
        )
        t_ret_end = time.perf_counter()
        retrieval_ms = (t_ret_end - t_ret_start) * 1000.0

        if not retrieved:
            total_ms = (time.perf_counter() - t0) * 1000.0
            return RAGResponse(
                query=question,
                answer="No relevant tickets found matching your operational parameters and region filter.",
                retrieved_chunks=[],
                cited_tickets=[],
                retrieval_time_ms=retrieval_ms,
                generation_time_ms=0.0,
                total_time_ms=total_ms,
            )

        # Step 3: Build Prompt Context
        context_blocks = []
        available_ticket_ids = set()
        for idx, chunk in enumerate(retrieved, start=1):
            tid = chunk.get("ticket_id", f"TICKET_{idx}")
            available_ticket_ids.add(tid)
            context_blocks.append(
                f"--- Context Record {idx} [Ticket: {tid}] (Circle: {chunk.get('circle')}, Category: {chunk.get('category')}) ---\n"
                f"{chunk.get('text')}\n"
            )

        context_str = "\n".join(context_blocks)
        user_prompt = (
            f"Context Information:\n{context_str}\n\n"
            f"User Inquiry: {question}\n\n"
            f"Provide a concise, accurate operational explanation citing the relevant ticket IDs."
        )

        # Step 4: Generation via LLM
        t_gen_start = time.perf_counter()
        raw_answer = self.llm_client.generate(
            prompt=user_prompt,
            system_prompt=SYSTEM_PROMPT,
            temperature=0.1,
            max_tokens=300,
        )
        t_gen_end = time.perf_counter()
        generation_ms = (t_gen_end - t_gen_start) * 1000.0
        total_ms = (time.perf_counter() - t0) * 1000.0

        # Step 5: Extract cited tickets for hallucination verification
        cited = [tid for tid in available_ticket_ids if tid in raw_answer]

        return RAGResponse(
            query=question,
            answer=raw_answer,
            retrieved_chunks=retrieved,
            cited_tickets=cited,
            retrieval_time_ms=retrieval_ms,
            generation_time_ms=generation_ms,
            total_time_ms=total_ms,
        )

