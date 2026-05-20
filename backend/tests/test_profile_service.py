from backend.data.schema import InteractionRecord
from backend.cache import TTLCache
from backend.services.profile_service import ProfileService


def test_profile_service_caches_results():
    cache = TTLCache(max_size=10, ttl_seconds=60)
    service = ProfileService(cache=cache)

    records = [
        InteractionRecord(
            user_id="u1",
            item_id="i1",
            rating=4.0,
            review_text="Nice",
            timestamp="2021-01-01",
            source="yelp",
        )
    ]

    first = service.build_profile_cached("u1", records)
    second = service.build_profile_cached("u1", records)

    assert first == second
    assert service.cache_size() == 1
