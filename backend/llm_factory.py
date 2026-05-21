from __future__ import annotations

from typing import Optional

from .config import app_config_from_env
from .llm_client import OpenAIClient


def create_openai_client() -> Optional[OpenAIClient]:
    config = app_config_from_env()
    if not config.enable_llm or not config.openai_api_key:
        return None

    return OpenAIClient(api_key=config.openai_api_key, model=config.openai_model)
