"""
Vector Store Interface using Qdrant.
Supports both remote Docker Qdrant (host:port) and embedded zero-dependency local disk storage.
Includes metadata filtering (Circle, Category) to simulate enterprise multi-tenant / RBAC isolation.
"""

from __future__ import annotations

import logging
import uuid
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

DEFAULT_COLLECTION = "telecom_support_tickets"
VECTOR_DIM = 384


class QdrantVectorStore:
    def __init__(
        self,
        host: Optional[str] = None,
        port: int = 6333,
        storage_path: Optional[str] = None,
        collection_name: str = DEFAULT_COLLECTION,
    ) -> None:
        self.collection_name = collection_name
        self.client = None
        self._init_client(host, port, storage_path)

    def _init_client(
        self,
        host: Optional[str],
        port: int,
        storage_path: Optional[str],
    ) -> None:
        try:
            from qdrant_client import QdrantClient
            from qdrant_client.models import Distance, VectorParams

            if host:
                logger.info("Connecting to Qdrant server at %s:%d", host, port)
                self.client = QdrantClient(host=host, port=port, timeout=10.0)
            elif storage_path:
                logger.info("Initializing embedded local Qdrant at %s", storage_path)
                self.client = QdrantClient(path=storage_path)
            else:
                logger.info("Initializing in-memory Qdrant client")
                self.client = QdrantClient(":memory:")

            # Ensure collection exists
            collections = self.client.get_collections().collections
            exists = any(c.name == self.collection_name for c in collections)
            if not exists:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=VECTOR_DIM, distance=Distance.COSINE),
                )
                logger.info("Created Qdrant collection '%s'", self.collection_name)

        except ImportError:
            logger.warning("qdrant-client not installed. Operating in lightweight in-memory fallback store.")
            self.client = None
            self._fallback_store: Dict[str, Dict[str, Any]] = {}

    def upsert_chunks(
        self,
        chunk_ids: List[str],
        ticket_ids: List[str],
        texts: List[str],
        circles: List[str],
        categories: List[str],
        vectors: List[List[float]],
        metadatas: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        """Upsert text chunks with embeddings and metadata payloads."""
        if not chunk_ids:
            return

        if self.client is None:
            # Fallback in-memory
            for i, cid in enumerate(chunk_ids):
                self._fallback_store[cid] = {
                    "ticket_id": ticket_ids[i],
                    "text": texts[i],
                    "circle": circles[i],
                    "category": categories[i],
                    "vector": vectors[i],
                    "metadata": (metadatas[i] if metadatas else {}),
                }
            return

        from qdrant_client.models import PointStruct

        points = []
        for i, cid in enumerate(chunk_ids):
            point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, cid))
            payload = {
                "chunk_id": cid,
                "ticket_id": ticket_ids[i],
                "text": texts[i],
                "circle": circles[i],
                "category": categories[i],
            }
            if metadatas and i < len(metadatas):
                payload.update(metadatas[i])

            points.append(PointStruct(id=point_id, vector=vectors[i], payload=payload))

        self.client.upsert(collection_name=self.collection_name, points=points)

    def delete_by_ticket_id(self, ticket_id: str) -> None:
        """CDC Delete handler: Purges all chunk vectors belonging to a deleted ticket."""
        if self.client is None:
            to_del = [k for k, v in self._fallback_store.items() if v.get("ticket_id") == ticket_id]
            for k in to_del:
                del self._fallback_store[k]
            return

        from qdrant_client.models import FieldCondition, Filter, MatchValue

        self.client.delete(
            collection_name=self.collection_name,
            points_selector=Filter(
                must=[
                    FieldCondition(
                        key="ticket_id",
                        match=MatchValue(value=ticket_id),
                    )
                ]
            ),
        )
        logger.info("Deleted all vectors for ticket_id='%s' from Qdrant", ticket_id)

    def search(
        self,
        query_vector: List[float],
        top_k: int = 5,
        circle: Optional[str] = None,
        category: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retrieves top_k nearest chunks, applying metadata filters to enforce RBAC/circle isolation.
        """
        if self.client is None:
            # Simple cosine similarity on fallback store
            results = []
            for cid, data in self._fallback_store.items():
                if circle and data["circle"] != circle:
                    continue
                if category and data["category"] != category:
                    continue
                # Dot product as vectors are normalized
                sim = sum(a * b for a, b in zip(query_vector, data["vector"]))
                results.append((sim, data))

            results.sort(key=lambda x: x[0], reverse=True)
            return [
                {
                    "score": s,
                    "chunk_id": d.get("chunk_id", cid),
                    "ticket_id": d["ticket_id"],
                    "circle": d["circle"],
                    "category": d["category"],
                    "text": d["text"],
                }
                for s, d in results[:top_k]
            ]

        from qdrant_client.models import FieldCondition, Filter, MatchValue

        filter_conditions = []
        if circle:
            filter_conditions.append(
                FieldCondition(key="circle", match=MatchValue(value=circle))
            )
        if category:
            filter_conditions.append(
                FieldCondition(key="category", match=MatchValue(value=category))
            )

        query_filter = Filter(must=filter_conditions) if filter_conditions else None

        search_results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            query_filter=query_filter,
            limit=top_k,
        )

        return [
            {
                "score": r.score,
                "chunk_id": r.payload.get("chunk_id"),
                "ticket_id": r.payload.get("ticket_id"),
                "circle": r.payload.get("circle"),
                "category": r.payload.get("category"),
                "text": r.payload.get("text"),
            }
            for r in search_results
        ]

