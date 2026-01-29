"""Unit tests for libretranslate.language module (performance-cached implementation)."""

import pytest
from unittest.mock import MagicMock, patch

import libretranslate.language as language_module


# --- iso2model ---


def test_iso2model_returns_lowercase_code_unchanged():
    assert language_module.iso2model("en") == "en"
    assert language_module.iso2model("fr") == "fr"


def test_iso2model_resolves_model_code_pt_br_to_pb():
    # iso2model: model code -> short code (rev_aliases)
    assert language_module.iso2model("pt-br") == "pb"
    assert language_module.iso2model("pt-BR") == "pb"


def test_iso2model_resolves_model_code_zh_hans_to_zh():
    assert language_module.iso2model("zh-hans") == "zh"


def test_iso2model_resolves_model_code_zh_hant_to_zt():
    assert language_module.iso2model("zh-hant") == "zt"


def test_iso2model_handles_list():
    assert language_module.iso2model(["en", "pt-br"]) == ["en", "pb"]


def test_iso2model_returns_non_string_unchanged():
    assert language_module.iso2model(123) == 123


# --- model2iso ---


def test_model2iso_returns_unknown_code_unchanged():
    assert language_module.model2iso("en") == "en"
    assert language_module.model2iso("xyz") == "xyz"


def test_model2iso_resolves_pb_to_pt_br():
    # model2iso: short code -> model code (aliases)
    assert language_module.model2iso("pb") == "pt-BR"
    assert language_module.model2iso("PB") == "pt-BR"


def test_model2iso_resolves_zh_to_zh_hans():
    assert language_module.model2iso("zh") == "zh-Hans"


def test_model2iso_resolves_zt_to_zh_hant():
    assert language_module.model2iso("zt") == "zh-Hant"


def test_model2iso_handles_list():
    assert language_module.model2iso(["en", "pb"]) == ["en", "pt-BR"]


def test_model2iso_handles_dict_with_language_key():
    result = language_module.model2iso({"language": "pb", "name": "Portuguese"})
    assert result == {"language": "pt-BR", "name": "Portuguese"}


# --- load_languages ---


@patch.object(language_module, "translate")
def test_load_languages_calls_get_installed_languages(mock_translate):
    mock_lang_en = MagicMock(code="en")
    mock_lang_es = MagicMock(code="es")
    mock_translate.get_installed_languages.return_value = [mock_lang_en, mock_lang_es]

    # Reset module cache so load_languages actually calls get_installed_languages
    language_module.__languages = None
    language_module.__lang_by_code = None

    result = language_module.load_languages()

    mock_translate.get_installed_languages.assert_called_once()
    assert result == [mock_lang_en, mock_lang_es]
    assert language_module.__lang_by_code == {"en": mock_lang_en, "es": mock_lang_es}


@patch.object(language_module, "translate")
def test_load_languages_returns_cached_list_on_second_call(mock_translate):
    mock_lang = MagicMock(code="en")
    mock_translate.get_installed_languages.return_value = [mock_lang]

    language_module.__languages = None
    language_module.__lang_by_code = None

    first = language_module.load_languages()
    second = language_module.load_languages()

    mock_translate.get_installed_languages.assert_called_once()
    assert first is second


# --- get_language_by_code ---


@patch.object(language_module, "translate")
def test_get_language_by_code_returns_language_when_found(mock_translate):
    mock_lang_en = MagicMock(code="en")
    mock_translate.get_installed_languages.return_value = [mock_lang_en]
    language_module.__languages = None
    language_module.__lang_by_code = None
    language_module.load_languages()

    result = language_module.get_language_by_code("en")

    assert result is mock_lang_en


@patch.object(language_module, "translate")
def test_get_language_by_code_returns_none_when_not_found(mock_translate):
    mock_translate.get_installed_languages.return_value = []
    language_module.__languages = []
    language_module.__lang_by_code = {}

    result = language_module.get_language_by_code("xx")

    assert result is None


# --- get_cached_translator ---


def test_get_cached_translator_caches_and_returns_translator():
    src = MagicMock(code="en")
    tgt = MagicMock(code="es")
    translator = MagicMock()
    src.get_translation.return_value = translator

    # Clear cache for predictable test
    language_module.__translator_cache = {}

    result = language_module.get_cached_translator(src, tgt)

    assert result is translator
    src.get_translation.assert_called_once_with(tgt)
    assert "en:es" in language_module.__translator_cache
    assert language_module.__translator_cache["en:es"] is translator


def test_get_cached_translator_returns_cached_on_second_call():
    src = MagicMock(code="en")
    tgt = MagicMock(code="es")
    translator = MagicMock()
    src.get_translation.return_value = translator
    language_module.__translator_cache = {}

    first = language_module.get_cached_translator(src, tgt)
    second = language_module.get_cached_translator(src, tgt)

    assert first is second
    src.get_translation.assert_called_once_with(tgt)


def test_get_cached_translator_returns_none_when_get_translation_returns_none():
    src = MagicMock(code="en")
    tgt = MagicMock(code="xx")
    src.get_translation.return_value = None
    language_module.__translator_cache = {}

    result = language_module.get_cached_translator(src, tgt)

    assert result is None
    assert "en:xx" not in language_module.__translator_cache


# --- load_lang_codes ---


@patch.object(language_module, "load_languages")
def test_load_lang_codes_returns_tuple_of_codes(mock_load_languages):
    mock_load_languages.return_value = [
        MagicMock(code="en"),
        MagicMock(code="es"),
    ]
    language_module.load_lang_codes.cache_clear()

    result = language_module.load_lang_codes()

    assert result == ("en", "es")
    mock_load_languages.assert_called()


# --- get_detector ---


@patch.object(language_module, "Detector")
@patch.object(language_module, "load_lang_codes", return_value=("en", "es"))
def test_get_detector_creates_and_caches_detector(mock_load_codes, mock_detector_class):
    language_module.__detector_instance = None

    detector = language_module.get_detector()

    mock_detector_class.assert_called_once_with(("en", "es"))
    assert detector is mock_detector_class.return_value


@patch.object(language_module, "Detector")
@patch.object(language_module, "load_lang_codes", return_value=("en",))
def test_get_detector_returns_same_instance_on_second_call(mock_load_codes, mock_detector_class):
    language_module.__detector_instance = None

    first = language_module.get_detector()
    second = language_module.get_detector()

    assert first is second
    mock_detector_class.assert_called_once()


# --- detect_languages ---


def _make_candidate(code, confidence, text_length=10):
    c = MagicMock()
    c.code = code
    c.confidence = confidence
    c.text_length = text_length
    return c


@patch.object(language_module, "get_detector")
def test_detect_languages_returns_list_of_confidence_and_language(mock_get_detector):
    mock_detector = MagicMock()
    mock_detector.detect.return_value = [_make_candidate("en", 0.95, 5)]
    mock_get_detector.return_value = mock_detector

    result = language_module.detect_languages("Hello")

    assert result == [{"confidence": 0.95, "language": "en"}]
    mock_detector.detect.assert_called_once_with("Hello")


@patch.object(language_module, "get_detector")
def test_detect_languages_returns_en_with_zero_confidence_when_no_candidates(mock_get_detector):
    mock_detector = MagicMock()
    mock_detector.detect.return_value = []
    mock_get_detector.return_value = mock_detector

    result = language_module.detect_languages("")

    assert result == [{"confidence": 0.0, "language": "en"}]


@patch.object(language_module, "get_detector")
def test_detect_languages_handles_batch_list(mock_get_detector):
    mock_detector = MagicMock()
    mock_detector.detect.side_effect = [
        [_make_candidate("en", 0.9, 5)],
        [_make_candidate("es", 0.85, 5)],
    ]
    mock_get_detector.return_value = mock_detector

    result = language_module.detect_languages(["Hello", "Hola"])

    assert len(result) >= 1
    assert mock_detector.detect.call_count == 2


@patch.object(language_module, "get_detector")
def test_detect_languages_sorts_by_confidence_times_text_length(mock_get_detector):
    mock_detector = MagicMock()
    c1 = _make_candidate("en", 0.5, 20)
    c2 = _make_candidate("es", 0.9, 5)
    mock_detector.detect.return_value = [c1, c2]
    mock_get_detector.return_value = mock_detector

    # Single string: code sets text_length = len(t) for each candidate, so both get 25
    result = language_module.detect_languages("x" * 25)

    # Total text_length 50; weighted scores 0.5*25/50=0.25, 0.9*25/50=0.45 -> es first
    assert len(result) == 2
    assert result[0]["language"] == "es"
    assert result[0]["confidence"] == 0.9
    assert result[1]["language"] == "en"
    assert result[1]["confidence"] == 0.5


# --- improve_translation_formatting ---


def test_improve_translation_formatting_empty_source_returns_empty():
    assert language_module.improve_translation_formatting("", "anything") == ""


def test_improve_translation_formatting_empty_translation_returns_source():
    assert language_module.improve_translation_formatting("Hello", "") == "Hello"


def test_improve_translation_formatting_strips_source():
    assert language_module.improve_translation_formatting("  hi  ", "hola") == "hola"


def test_improve_translation_formatting_copies_final_punctuation_from_source():
    result = language_module.improve_translation_formatting(
        "Hello!", "Bonjour.", improve_punctuation=True
    )
    assert result == "Bonjour!"


def test_improve_translation_formatting_removes_trailing_punctuation_when_source_has_none():
    result = language_module.improve_translation_formatting(
        "Hello", "Bonjour.", improve_punctuation=True
    )
    assert result == "Bonjour"


def test_improve_translation_formatting_preserves_lowercase():
    result = language_module.improve_translation_formatting("hello", "BONJOUR")
    assert result == "bonjour"


def test_improve_translation_formatting_preserves_uppercase():
    result = language_module.improve_translation_formatting("HELLO", "bonjour")
    assert result == "BONJOUR"


def test_improve_translation_formatting_preserves_capitalized():
    result = language_module.improve_translation_formatting("Hello", "bonjour")
    assert result == "Bonjour"


def test_improve_translation_formatting_single_word_duplicate_removal():
    # Single word source, translation with repeated word -> collapse to single word
    result = language_module.improve_translation_formatting(
        "salad", "salad salad salad", remove_single_word_duplicates=True
    )
    assert result == "salad"


def test_improve_translation_formatting_single_word_no_duplicate_unchanged():
    result = language_module.improve_translation_formatting(
        "hi", "hola amigo", remove_single_word_duplicates=True
    )
    assert result == "hola amigo"


def test_improve_translation_formatting_punctuation_disabled():
    result = language_module.improve_translation_formatting(
        "Hello!", "Bonjour.", improve_punctuation=False
    )
    assert result == "Bonjour."


def test_improve_translation_formatting_chinese_period():
    result = language_module.improve_translation_formatting(
        "你好。", "Hello.", improve_punctuation=True
    )
    assert result == "Hello。"
