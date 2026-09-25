from types import SimpleNamespace

from libretranslate.detect import Detector, Language, normalized_lang_code


def test_language_attributes():
    lang = Language("en", 95)
    assert lang.code == "en"
    assert lang.confidence == 95.0


def test_normalized_lang_code_chinese():
    assert normalized_lang_code(SimpleNamespace(lang="zh-cn")) == "zh"
    assert normalized_lang_code(SimpleNamespace(lang="zh-tw")) == "zt"
    assert normalized_lang_code(SimpleNamespace(lang="en")) == "en"


def test_detect_english():
    results = Detector(("en", "es")).detect(
        "This is a fairly long English sentence used to test language detection."
    )
    assert results[0].code == "en"
    assert results[0].confidence > 0


def test_detect_spanish():
    results = Detector(("en", "es")).detect(
        "Esta es una oración bastante larga en español utilizada para probar la detección de idiomas."
    )
    assert results[0].code == "es"
    assert results[0].confidence > 0


def test_detect_filters_to_supported_languages():
    results = Detector(("es",)).detect(
        "This is a fairly long English sentence used to test language detection."
    )
    assert results[0].code == "en"
    assert results[0].confidence == 0


def test_detect_undetectable_returns_english_fallback():
    results = Detector(("en", "es")).detect("")
    assert results[0].code == "en"
    assert results[0].confidence == 0
