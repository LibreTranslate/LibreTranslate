from libretranslate.locales import (
    get_alternate_locale_links,
    get_available_locale_codes,
    get_available_locales,
    swag_eval,
)


def test_get_available_locales_contains_english():
    locales = get_available_locales()
    codes = [l["code"] for l in locales]
    assert "en" in codes
    assert len(locales) > 1


def test_get_available_locales_reviewed_flag():
    for locale in get_available_locales(only_reviewed=True):
        assert locale["reviewed"] is True


def test_get_available_locales_sorted():
    locales = get_available_locales(sort_by_name=True)
    names = [l["name"] for l in locales]
    assert names == sorted(names)


def test_get_available_locale_codes():
    codes = get_available_locale_codes()
    assert "en" in codes
    assert all(isinstance(c, str) for c in codes)


def test_get_alternate_locale_links_empty_by_default(monkeypatch):
    get_alternate_locale_links.cache_clear()
    monkeypatch.delenv("LT_LOCALE_LINK_TEMPLATE", raising=False)
    assert get_alternate_locale_links() == []


def test_get_alternate_locale_links(monkeypatch):
    get_alternate_locale_links.cache_clear()
    monkeypatch.setenv("LT_LOCALE_LINK_TEMPLATE", "https://{LANG}.example.com")

    try:
        links = get_alternate_locale_links()
        en_link = next(l for l in links if l["lang"] == "en")
        # The apex domain drops the "en." subdomain
        assert en_link["link"] == "https://example.com"

        es_link = next(l for l in links if l["lang"] == "es")
        assert es_link["link"] == "https://es.example.com"
    finally:
        get_alternate_locale_links.cache_clear()


def test_swag_eval_applies_func_to_summary_and_description():
    swag = {
        "paths": {
            "/translate": {
                "summary": "translate text",
                "description": "translates text",
                "consumes": ["leave me", "alone"],
                "parameters": [{"description": "nested"}],
            }
        },
        "tags": ["translate"],
    }

    result = swag_eval(swag, str.upper)

    assert result["paths"]["/translate"]["summary"] == "TRANSLATE TEXT"
    assert result["paths"]["/translate"]["description"] == "TRANSLATES TEXT"
    assert result["paths"]["/translate"]["parameters"][0]["description"] == "NESTED"
    assert result["tags"] == ["TRANSLATE"]
    # 'consumes' lists are never translated
    assert result["paths"]["/translate"]["consumes"] == ["leave me", "alone"]
