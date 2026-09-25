import json

import pytest

from libretranslate import cache, storage


@pytest.fixture()
def mem_storage():
    return storage.setup("memory://")


def test_disabled_by_default(mem_storage):
    c = cache.setup("")
    assert not c.enabled
    assert not c.should_check("any-key")


def test_should_check_all(mem_storage):
    c = cache.setup(["all"])
    assert c.should_check("any-key")
    assert c.should_check(None)


def test_should_check_specific_keys(mem_storage):
    c = cache.setup(["key1", "key2"])
    assert c.should_check("key1")
    assert c.should_check("key2")
    assert not c.should_check("other")


def test_hit_miss(mem_storage):
    c = cache.setup(["all"])
    cache_key, hit = c.hit("hello", "en", "es", "text", 0)
    assert hit is None


def test_cache_roundtrip(mem_storage):
    c = cache.setup(["all"])
    cache_key, _ = c.hit("hello", "en", "es", "text", 0)

    c.cache(cache_key, {"translatedText": "hola"})

    same_key, hit = c.hit("hello", "en", "es", "text", 0)
    assert same_key == cache_key
    assert json.loads(hit) == {"translatedText": "hola"}


def test_cache_key_depends_on_inputs(mem_storage):
    c = cache.setup(["all"])
    k1, _ = c.hit("hello", "en", "es", "text", 0)
    k2, _ = c.hit("hello", "en", "fr", "text", 0)
    k3, _ = c.hit("hello", "en", "es", "html", 0)
    k4, _ = c.hit("hello", "en", "es", "text", 1)
    k5, _ = c.hit("goodbye", "en", "es", "text", 0)

    assert len({k1, k2, k3, k4, k5}) == 5


def test_cache_non_dict_content(mem_storage):
    c = cache.setup(["all"])
    cache_key, _ = c.hit("hello", "en", "es", "text", 0)

    c.cache(cache_key, "plain string")

    _, hit = c.hit("hello", "en", "es", "text", 0)
    assert hit == "plain string"


def test_batch_texts_share_cache_key(mem_storage):
    c = cache.setup(["all"])
    k1, _ = c.hit(["a", "b"], "en", "es", "text", 0)
    k2, _ = c.hit("a|b", "en", "es", "text", 0)
    assert k1 == k2
