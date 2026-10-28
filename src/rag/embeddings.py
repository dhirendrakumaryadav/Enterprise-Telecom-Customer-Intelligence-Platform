"""
Embedding Generation Module using SentenceTransformers.
Default: 'BAAI/bge-small-en-v1.5' (384-dimensional, highly efficient on CPU/GPU).
Alternative: 'sentence-transformers/all-MiniLM-L6-v2'.
"""

from __future__ import annotations

import hashlib
import logging
from typing import List

logger = logging.getLogger(__name__)

EMBEDDING_DIM = 384


class EmbeddingService:
    def __init__(
        self,
        model_name: str = "BAAI/bge-small-en-v1.5",
        device: str = "auto",
        batch_size: int = 32,
    ) -> None:
        self.model_name = model_name
        self.batch_size = batch_size
        self._model = None
        self._is_mock = False
        self._init_model(device)

    def _init_model(self, device: str) -> None:
        try:
            import torch
            from sentence_transformers import SentenceTransformer

            if device == "auto":
                target_device = "cuda" if torch.cuda.is_available() else "cpu"
            else:
                target_device = device

            logger.info("Loading embedding model '%s' on %s", self.model_name, target_device)
            self._model = SentenceTransformer(self.model_name, device=target_device)
        except ImportError:
            logger.warning(
                "sentence_transformers or torch not installed. Running in deterministic hash-embedding mode."
            )
            self._is_mock = True

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of text strings into normalized 384-d vectors."""
        if not texts:
            return []

        if self._is_mock or self._model is None:
            return [self._mock_vector(t) for t in texts]

        embeddings = self._model.encode(
            texts,
            batch_size=self.batch_size,
            show_progress_bar=False,
            normalize_embeddings=True,
        )
        return embeddings.tolist()

    def embed_query(self, query: str) -> List[float]:
        """Embed a single search query."""
        results = self.embed_texts([query])
        return results[0]

    def _mock_vector(self, text: str) -> List[float]:
        """Produces a deterministic unit vector from text hash for offline testing."""
        h = hashlib.sha256(text.encode("utf-8")).digest()
        raw = [(float(b) / 255.0) - 0.5 for b in h]
        # Repeat/pad to 384 dimensions
        vector = (raw * ((EMBEDDING_DIM // len(raw)) + 1))[:EMBEDDING_DIM]
        norm = sum(x * x for x in vector) ** 0.5 or 1.0
        return [x / norm for x in vector]

