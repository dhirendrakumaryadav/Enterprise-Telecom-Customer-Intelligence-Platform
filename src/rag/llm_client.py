"""
LLM Client Interface and Ollama Implementation.
Designed with an abstract base class to guarantee vendor neutrality:
Ollama (local 3B/4B 4-bit) as core, with pluggable cloud adapters for optional deployment.
"""

from __future__ import annotations

import json
import logging
import urllib.request
import urllib.error
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class BaseLLMClient(ABC):
    """Abstract interface for all LLM providers."""

    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 512,
    ) -> str:
        """Generate text completion from prompt."""
        pass


class OllamaClient(BaseLLMClient):
    """
    Local Ollama API Client.
    Communicates with Ollama running natively on Windows host or inside container network.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "llama3.2:3b",
        timeout_seconds: int = 60,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout_seconds = timeout_seconds

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 512,
    ) -> str:
        url = f"{self.base_url}/api/generate"

        payload: Dict[str, Any] = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }

        if system_prompt:
            payload["system"] = system_prompt

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=self.timeout_seconds) as response:
                if response.status == 200:
                    result = json.loads(response.read().decode("utf-8"))
                    return result.get("response", "").strip()
                else:
                    raise RuntimeError(f"Ollama returned HTTP status {response.status}")
        except urllib.error.URLError as e:
            logger.error("Failed to connect to Ollama at %s: %s", self.base_url, e)
            raise ConnectionError(
                f"Cannot connect to Ollama at {self.base_url}. Ensure 'ollama run {self.model}' is active."
            ) from e


class MockLLMClient(BaseLLMClient):
    """Deterministic mock client for offline CI testing and unit tests."""

    def __init__(self, fixed_response: Optional[str] = None) -> None:
        self.fixed_response = fixed_response or "Mock answer based on retrieved context."

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 512,
    ) -> str:
        return self.fixed_response

