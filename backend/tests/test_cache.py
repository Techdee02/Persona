from backend.cache import TTLCache


def test_cache_set_get_and_eviction():
    cache = TTLCache(max_size=2, ttl_seconds=60)
    cache.set("a", 1)
    cache.set("b", 2)
    assert cache.get("a") == 1

    cache.set("c", 3)
    assert cache.get("b") is None
    assert cache.get("a") == 1
