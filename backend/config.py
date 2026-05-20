from dataclasses import dataclass
import os


@dataclass(frozen=True)
class DatasetPaths:
    yelp: str
    amazon: str
    goodreads: str


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
