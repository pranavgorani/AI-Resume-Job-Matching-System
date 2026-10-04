import json
import logging
from typing import Optional, Dict, Any
from app.config import settings

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        pass

    def is_available(self) -> bool:
        from services.ai import get_ai_coordinator
        coord = get_ai_coordinator()
        return coord.get_primary().is_available() or coord.get_fallback().is_available()

    def generate_text(self, prompt: str, system_instruction: Optional[str] = None) -> Optional[str]:
        from services.ai import get_ai_coordinator
        try:
            return get_ai_coordinator().generate_text(prompt, system_instruction)
        except Exception as e:
            logger.error(f"AI text generation error: {type(e).__name__}")
            return None

    def generate_json(self, prompt: str, system_instruction: Optional[str] = None) -> Optional[Dict[str, Any]]:
        from services.ai import get_ai_coordinator
        try:
            return get_ai_coordinator().generate_json(prompt, system_instruction)
        except Exception as e:
            logger.error(f"AI JSON generation error: {type(e).__name__}")
            return None

gemini_service = GeminiService()
