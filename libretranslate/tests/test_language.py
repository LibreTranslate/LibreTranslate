from types import SimpleNamespace

from libretranslate.language import (
    get_language_with_fallback,
    improve_translation_formatting,
    iso2model,
    model2iso,
)


def test_iso2model():
    assert iso2model("pt-BR") == "pb"
    assert iso2model("zh-Hans") == "zh"
    assert iso2model("zh-Hant") == "zt"
    assert iso2model("en") == "en"


def test_iso2model_is_case_insensitive():
    assert iso2model("PT-br") == "pb"


def test_iso2model_list():
    assert iso2model(["en", "pt-BR"]) == ["en", "pb"]


def test_iso2model_non_string_passthrough():
    assert iso2model(None) is None


def test_model2iso():
    assert model2iso("pb") == "pt-BR"
    assert model2iso("zh") == "zh-Hans"
    assert model2iso("zt") == "zh-Hant"
    assert model2iso("en") == "en"


def test_model2iso_list():
    assert model2iso(["en", "pb"]) == ["en", "pt-BR"]


def test_model2iso_dict():
    assert model2iso({"language": "zh", "confidence": 90}) == {
        "language": "zh-Hans",
        "confidence": 90,
    }


def test_get_language_with_fallback_exact_match():
    en = SimpleNamespace(code="en")
    assert get_language_with_fallback("en", [en]) is en


def test_get_language_with_fallback_variant():
    pt = SimpleNamespace(code="pt")
    assert get_language_with_fallback("pb", [pt]) is pt


def test_get_language_with_fallback_no_match():
    en = SimpleNamespace(code="en")
    assert get_language_with_fallback("fr", [en]) is None


def test_improve_translation_formatting_adds_punctuation():
    assert improve_translation_formatting("Hello.", "hola") == "Hola."


def test_improve_translation_formatting_replaces_punctuation():
    assert improve_translation_formatting("Hello!", "hola?") == "Hola!"


def test_improve_translation_formatting_removes_punctuation():
    assert improve_translation_formatting("Hello", "hola.") == "Hola"


def test_improve_translation_formatting_lowercase_source():
    assert improve_translation_formatting("hello", "Hola") == "hola"


def test_improve_translation_formatting_uppercase_source():
    assert improve_translation_formatting("HELLO", "hola") == "HOLA"


def test_improve_translation_formatting_capitalized_source():
    assert improve_translation_formatting("Hello", "hola") == "Hola"


def test_improve_translation_formatting_empty_source():
    assert improve_translation_formatting("   ", "hola") == ""


def test_improve_translation_formatting_empty_translation():
    assert improve_translation_formatting("hello", "") == "hello"


def test_improve_translation_formatting_single_word_duplicates():
    # Workaround for the "salad" bug (issue #46)
    assert improve_translation_formatting("cat", "gato gato gato gato") == "gato"


def test_filter_unique():
    from libretranslate.app import filter_unique

    assert filter_unique(["a", "b", "a", "c"], "extra") == ["a", "b", "c"]


def test_filter_unique_excludes_extra_and_empty():
    from libretranslate.app import filter_unique

    assert filter_unique(["a", "extra", "", "b"], "extra") == ["a", "b"]


def test_detect_translatable():
    from libretranslate.app import detect_translatable

    assert detect_translatable("Hello") is True
    assert detect_translatable("😀") is False
    assert detect_translatable(["😀", "😁"]) is False
    assert detect_translatable(["😀", "Hello"]) is True
