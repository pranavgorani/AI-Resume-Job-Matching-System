import abc
import json
import logging
import re
import time
import hashlib
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger("talentproof.ai")

class AIProvider(abc.ABC):
    """
    Abstract Base Class for AI Providers.
    Implementations include GeminiProvider (Primary) and HuggingFaceProvider (Fallback).
    """

    @property
    @abc.abstractmethod
    def provider_name(self) -> str:
        """Name of the provider (e.g., 'gemini', 'huggingface')."""
        pass

    @abc.abstractmethod
    def is_available(self) -> bool:
        """Check if provider is configured and credentials are present."""
        pass

    @abc.abstractmethod
    def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.2,
        max_output_tokens: int = 4096
    ) -> str:
        """Generate text from prompt."""
        pass

    @abc.abstractmethod
    def generate_json(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.1
    ) -> Dict[str, Any]:
        """Generate structured JSON output from prompt."""
        pass

    @abc.abstractmethod
    def generate_embeddings(
        self,
        texts: Union[str, List[str]]
    ) -> List[List[float]]:
        """Generate vector embeddings for text(s)."""
        pass

    @staticmethod
    def clean_json_string(text: str) -> str:
        """Helper to extract JSON object/array from markdown fences or messy response."""
        cleaned = text.strip()
        # Remove markdown code blocks if present
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        # If still not valid, try finding outermost curly or square braces
        match = re.search(r"(\{.*\}|\[.*\])", cleaned, re.DOTALL)
        if match:
            cleaned = match.group(0)
        return cleaned


class ResilientAICoordinator:
    """
    Coordinates primary (Gemini) and fallback (Hugging Face) AI providers.
    Implements retry with exponential backoff and transparent caching.
    """
    def __init__(self):
        self._gemini: Optional[AIProvider] = None
        self._huggingface: Optional[AIProvider] = None
        self._cache: Dict[str, Any] = {}

    def _get_cache_key(self, prefix: str, data: str) -> str:
        content_hash = hashlib.sha256(data.encode("utf-8")).hexdigest()
        return f"{prefix}:{content_hash}"

    def get_primary(self) -> AIProvider:
        if self._gemini is None:
            from .gemini_service import GeminiProvider
            self._gemini = GeminiProvider()
        return self._gemini

    def get_fallback(self) -> AIProvider:
        if self._huggingface is None:
            from .huggingface_service import HuggingFaceProvider
            self._huggingface = HuggingFaceProvider()
        return self._huggingface

    def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.2
    ) -> str:
        cache_key = self._get_cache_key("text", f"{prompt}:{system_instruction}")
        if cache_key in self._cache:
            return self._cache[cache_key]

        primary = self.get_primary()
        fallback = self.get_fallback()

        # Try Gemini (Primary) with exponential backoff
        if primary.is_available():
            for attempt in range(2):
                try:
                    res = primary.generate_text(prompt, system_instruction, temperature)
                    if res:
                        self._cache[cache_key] = res
                        return res
                except Exception as e:
                    logger.warning(f"Gemini attempt {attempt + 1} failed: {type(e).__name__}. Retrying...")
                    time.sleep(1.0 * (2 ** attempt))

        # Fallback to Hugging Face
        if fallback.is_available():
            logger.info("Failing over to Hugging Face fallback provider...")
            try:
                res = fallback.generate_text(prompt, system_instruction, temperature)
                if res:
                    self._cache[cache_key] = res
                    return res
            except Exception as e:
                logger.error(f"Hugging Face fallback failed: {type(e).__name__}")

        raise RuntimeError("AI service temporarily unavailable. Please retry in a few moments.")

    def generate_json(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.1
    ) -> Dict[str, Any]:
        cache_key = self._get_cache_key("json", f"{prompt}:{system_instruction}")
        if cache_key in self._cache:
            return self._cache[cache_key]

        primary = self.get_primary()
        fallback = self.get_fallback()

        # Try Gemini
        if primary.is_available():
            for attempt in range(2):
                try:
                    res = primary.generate_json(prompt, system_instruction, temperature)
                    if res:
                        self._cache[cache_key] = res
                        return res
                except Exception as e:
                    logger.warning(f"Gemini JSON attempt {attempt + 1} failed: {type(e).__name__}. Retrying...")
                    time.sleep(1.0 * (2 ** attempt))

        # Fallback to Hugging Face
        if fallback.is_available():
            logger.info("Failing over to Hugging Face fallback provider for JSON generation...")
            try:
                res = fallback.generate_json(prompt, system_instruction, temperature)
                if res:
                    self._cache[cache_key] = res
                    return res
            except Exception as e:
                logger.error(f"Hugging Face fallback failed: {type(e).__name__}")

        raise RuntimeError("AI analysis temporarily unavailable. Please verify API configuration or try again.")

    def generate_embeddings(
        self,
        texts: Union[str, List[str]]
    ) -> List[List[float]]:
        primary = self.get_primary()
        fallback = self.get_fallback()

        if primary.is_available():
            try:
                return primary.generate_embeddings(texts)
            except Exception as e:
                logger.warning(f"Gemini embeddings failed: {type(e).__name__}. Trying fallback...")

        if fallback.is_available():
            try:
                return fallback.generate_embeddings(texts)
            except Exception as e:
                logger.error(f"Hugging Face embeddings failed: {type(e).__name__}")

        # Deterministic local fallback embeddings
        from .embedding_service import generate_deterministic_embedding
        if isinstance(texts, str):
            return [generate_deterministic_embedding(texts)]
        return [generate_deterministic_embedding(t) for t in texts]


# Global singleton instance
ai_coordinator = ResilientAICoordinator()

def get_ai_coordinator() -> ResilientAICoordinator:
    return ai_coordinator
