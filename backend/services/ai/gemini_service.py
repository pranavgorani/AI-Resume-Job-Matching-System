import json
import logging
import os
import time
from typing import Any, Dict, List, Optional, Union

from .ai_provider import AIProvider

logger = logging.getLogger("talentproof.ai.gemini")

class GeminiProvider(AIProvider):
    """
    Primary AI Provider using Google Gemini API (gemini-2.5-flash / text-embedding-004).
    """
    def __init__(self):
        self._api_key = os.getenv("GEMINI_API_KEY", os.getenv("GOOGLE_API_KEY", ""))
        self._model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        self._embedding_model = os.getenv("GEMINI_EMBEDDING_MODEL", "text-embedding-004")
        self._client = None

        if self._api_key:
            try:
                from google import genai
                self._client = genai.Client(api_key=self._api_key)
            except Exception as e:
                logger.warning(f"Failed to initialize google-genai Client: {type(e).__name__}")
                self._client = None

    @property
    def provider_name(self) -> str:
        return "gemini"

    def is_available(self) -> bool:
        return self._client is not None and bool(self._api_key)

    def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.2,
        max_output_tokens: int = 4096
    ) -> str:
        if not self.is_available():
            raise RuntimeError("Gemini provider is not available or API key is not configured.")

        from google.genai import types
        config = types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            system_instruction=system_instruction if system_instruction else None,
        )

        response = self._client.models.generate_content(
            model=self._model,
            contents=prompt,
            config=config,
        )

        if not response or not response.text:
            raise RuntimeError("Gemini returned empty response.")
        return response.text.strip()

    def generate_json(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.1
    ) -> Dict[str, Any]:
        if not self.is_available():
            raise RuntimeError("Gemini provider is not available or API key is not configured.")

        from google.genai import types
        config = types.GenerateContentConfig(
            temperature=temperature,
            response_mime_type="application/json",
            system_instruction=system_instruction if system_instruction else None,
        )

        response = self._client.models.generate_content(
            model=self._model,
            contents=prompt,
            config=config,
        )

        if not response or not response.text:
            raise RuntimeError("Gemini returned empty JSON response.")

        clean_text = self.clean_json_string(response.text)
        try:
            return json.loads(clean_text)
        except json.JSONDecodeError as err:
            logger.warning(f"JSON decode error from Gemini: {err}. Attempting secondary recovery.")
            # Secondary cleanup
            clean_text = clean_text.replace("\n", " ")
            return json.loads(clean_text)

    def generate_embeddings(
        self,
        texts: Union[str, List[str]]
    ) -> List[List[float]]:
        if not self.is_available():
            raise RuntimeError("Gemini provider is not available or API key is not configured.")

        input_list = [texts] if isinstance(texts, str) else texts
        if not input_list:
            return []

        try:
            # google-genai embed_content
            response = self._client.models.embed_content(
                model=self._embedding_model,
                contents=input_list,
            )
            # Response may have embeddings attribute
            if hasattr(response, "embeddings") and response.embeddings:
                return [e.values for e in response.embeddings]
            elif hasattr(response, "embedding") and response.embedding:
                return [response.embedding.values]
            raise ValueError("Unexpected response structure from embed_content")
        except Exception as e:
            logger.warning(f"Gemini embed_content call failed: {type(e).__name__}")
            raise
