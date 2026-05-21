from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional

logger = logging.getLogger("persona.llm_client")

_RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}
_MAX_RETRIES = 3
_BASE_DELAY = 1.0  # seconds; doubled on each retry


class OpenAIClient:
    def __init__(self, api_key: str, model: str) -> None:
        if not api_key:
            raise ValueError("OpenAI API key is required")
        self._api_key = api_key
        self._model = model

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[str] = None,
        temperature: float = 0.2,
    ) -> Dict[str, Any]:
        from openai import OpenAI, RateLimitError, APIStatusError

        client = OpenAI(api_key=self._api_key)
        delay = _BASE_DELAY

        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                response = client.chat.completions.create(
                    model=self._model,
                    messages=messages,
                    tools=tools,
                    tool_choice=tool_choice,
                    temperature=temperature,
                )
                return response.model_dump()

            except RateLimitError as exc:
                if attempt == _MAX_RETRIES:
                    raise
                logger.warning("Rate limited (attempt %d/%d); retrying in %.1fs", attempt, _MAX_RETRIES, delay)
                time.sleep(delay)
                delay *= 2

            except APIStatusError as exc:
                if exc.status_code not in _RETRYABLE_STATUS_CODES or attempt == _MAX_RETRIES:
                    raise
                logger.warning(
                    "API error %d (attempt %d/%d); retrying in %.1fs",
                    exc.status_code, attempt, _MAX_RETRIES, delay,
                )
                time.sleep(delay)
                delay *= 2
