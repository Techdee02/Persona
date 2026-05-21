from dataclasses import dataclass
import os


@dataclass(frozen=True)
class DatasetPaths:
    yelp: str
    amazon: str
    goodreads: str


@dataclass(frozen=True)
class AppConfig:
    deterministic_mode: bool
    profile_cache_ttl_seconds: int
    profile_cache_max_size: int
    enable_llm: bool
    openai_api_key: str
    openai_model: str
    vector_store_path: str


def _get_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ValueError(f"Missing required env var: {name}")
    return value


def dataset_paths_from_env() -> DatasetPaths:
    return DatasetPaths(
        yelp=_get_env("DATASET_YELP_PATH"),
        amazon=_get_env("DATASET_AMAZON_PATH"),
        goodreads=_get_env("DATASET_GOODREADS_PATH"),
    )


def app_config_from_env() -> AppConfig:
    return AppConfig(
        deterministic_mode=_get_bool_env("DETERMINISTIC_MODE", default=False),
        profile_cache_ttl_seconds=_get_int_env("PROFILE_CACHE_TTL_SECONDS", default=3600),
        profile_cache_max_size=_get_int_env("PROFILE_CACHE_MAX_SIZE", default=1000),
        enable_llm=_get_bool_env("ENABLE_LLM", default=False),
        openai_api_key=os.getenv("OPENAI_API_KEY", "").strip(),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4o"),
        vector_store_path=os.getenv("VECTOR_STORE_PATH", "").strip(),
    )


def _get_int_env(name: str, default: int) -> int:
    value = os.getenv(name, "").strip()
    if not value:
        return default
    return int(value)


def _get_bool_env(name: str, default: bool) -> bool:
    value = os.getenv(name, "").strip().lower()
    if not value:
        return default
    return value in {"1", "true", "yes", "y"}
