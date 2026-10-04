import json
import logging
import os
from typing import Any, Dict, List, Optional, Union

from .ai_provider import AIProvider

logger = logging.getLogger("talentproof.ai.huggingface")

class HuggingFaceProvider(AIProvider):
    """
    Fallback AI Provider using Hugging Face Inference API.
    Used seamlessly when Gemini reaches limits, errors, or is unavailable.
    """
    def __init__(self):
        self._token = os.getenv("HF_TOKEN", "")
        self._model = os.getenv("HF_MODEL", "meta-llama/Llama-3.1-8B-Instruct")
        self._embedding_model = os.getenv("HF_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        self._client = None

        if self._token:
            try:
                from huggingface_hub import InferenceClient
                self._client = InferenceClient(token=self._token)
            except Exception as e:
                logger.warning(f"Failed to initialize HuggingFace InferenceClient: {type(e).__name__}")
                self._client = None

    @property
    def provider_name(self) -> str:
        return "huggingface"

    def is_available(self) -> bool:
        return self._client is not None and bool(self._token)

    def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.2,
        max_output_tokens: int = 2048
    ) -> str:
        if not self.is_available():
            raise RuntimeError("Hugging Face provider is not configured.")

        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})

        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_output_tokens,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.warning(f"Hugging Face chat completion failed: {type(e).__name__}")
            # Try text_generation fallback
            try:
                full_prompt = f"{system_instruction}\n\n{prompt}" if system_instruction else prompt
                res = self._client.text_generation(
                    full_prompt,
                    model=self._model,
                    max_new_tokens=max_output_tokens,
                    temperature=temperature
                )
                return res.strip()
            except Exception as err2:
                logger.error(f"Hugging Face text_generation also failed: {type(err2).__name__}")
                raise

    def generate_json(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.1
    ) -> Dict[str, Any]:
        enhanced_prompt = (
            f"{prompt}\n\n"
            f"CRITICAL INSTRUCTION: Return ONLY a valid JSON object matching the requested schema. "
            f"Do not include any commentary, Markdown formatting, or explanation before or after the JSON."
        )
        raw_text = self.generate_text(
            enhanced_prompt,
            system_instruction=system_instruction or "You are an AI that outputs strictly valid JSON.",
            temperature=temperature
        )

        cleaned = self.clean_json_string(raw_text)
        return json.loads(cleaned)

    def generate_embeddings(
        self,
        texts: Union[str, List[str]]
    ) -> List[List[float]]:
        if not self.is_available():
            raise RuntimeError("Hugging Face provider is not configured.")

        input_list = [texts] if isinstance(texts, str) else texts
        if not input_list:
            return []

        try:
            # Call feature_extraction
            res = self._client.feature_extraction(
                text=input_list,
                model=self._embedding_model
            )
            # res may be a numpy array or nested list
            if hasattr(res, "tolist"):
                return res.tolist()
            elif isinstance(res, list):
                if isinstance(res[0], list):
                    return res
                return [res]
            raise ValueError("Unexpected feature_extraction return format")
        except Exception as e:
            logger.warning(f"Hugging Face embedding extraction failed: {type(e).__name__}")
            raise
