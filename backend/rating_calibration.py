from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .data.schema import InteractionRecord


@dataclass(frozen=True)
class RatingCalibration:
    user_mean: float
    user_std: float
    population_mean: float
    population_std: float

    def calibrate(self, rating: float) -> float:
        if self.user_std == 0 or self.population_std == 0:
            return rating

        z_score = (rating - self.user_mean) / self.user_std
        calibrated = self.population_mean + z_score * self.population_std
        return max(1.0, min(5.0, calibrated))


def build_rating_calibration(
    user_records: Iterable[InteractionRecord],
    population_records: Iterable[InteractionRecord],
) -> RatingCalibration:
    user_ratings = [record.rating for record in user_records]
    population_ratings = [record.rating for record in population_records]

    user_mean, user_std = _mean_std(user_ratings)
    population_mean, population_std = _mean_std(population_ratings)

    return RatingCalibration(
        user_mean=user_mean,
        user_std=user_std,
        population_mean=population_mean,
        population_std=population_std,
    )


def _mean_std(values: list[float]) -> tuple[float, float]:
    if not values:
        return 0.0, 0.0

    mean_val = sum(values) / len(values)
    if len(values) < 2:
        return mean_val, 0.0

    variance = sum((value - mean_val) ** 2 for value in values) / len(values)
    return mean_val, variance ** 0.5
