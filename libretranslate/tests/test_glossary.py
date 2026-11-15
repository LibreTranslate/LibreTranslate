import json
import os
import tempfile
import pytest

from libretranslate import glossary
from libretranslate.glossary import (
    Glossary,
    mask_terms,
    unmask_terms,
    validate_glossary,
    merge_glossaries,
    load_server_glossaries,
    get_server_glossary,
    setup,
)


def test_sorting_multi_word_phrases_before_substrings():
    terms = {
        "machine translation": "TAO",
        "machine": "máquina",
    }
    text = "I study machine translation and machine learning."
    masked, placeholders = mask_terms(text, terms)

    # "machine translation" must be masked as a single unit before "machine"
    assert "LTPH0" in masked
    assert "LTPH1" in masked

    restored = unmask_terms(masked, placeholders)
    assert restored == "I study TAO and máquina learning."


def test_custom_placeholder_prefix():
    terms = {"machine translation": "TAO", "machine": "máquina"}
    text = "I study machine translation and machine learning."
    masked, placeholders = mask_terms(text, terms, placeholder_prefix="LTGLOSSARY")

    assert "LTGLOSSARY0" in masked
    assert "LTGLOSSARY1" in masked

    restored = unmask_terms(masked, placeholders)
    assert restored == "I study TAO and máquina learning."


def test_boundary_aware_matching():
    terms = {"cat": "gato"}
    text = "The cat is in the catalog and bobcat is wild."
    masked, placeholders = mask_terms(text, terms)

    # Only whole-word "cat" should match, not "catalog" or "bobcat"
    assert "catalog" in masked
    assert "bobcat" in masked

    restored = unmask_terms(masked, placeholders)
    assert restored == "The gato is in the catalog and bobcat is wild."


def test_special_regex_characters_in_terms():
    terms = {
        "C++": "C plus plus",
        ".NET": "punto NET",
        "price ($5)": "precio ($5)",
        "A* search": "búsqueda A*",
        "[special]": "especial",
    }
    text = "Code in C++ and .NET using A* search for price ($5) with [special]."
    masked, placeholders = mask_terms(text, terms)
    restored = unmask_terms(masked, placeholders)

    assert restored == "Code in C plus plus and punto NET using búsqueda A* for precio ($5) with especial."


def test_case_sensitivity_configuration():
    terms = {"Apple": "Manzana"}

    # Case-insensitive by default
    text = "I ate an apple, an Apple, and an APPLE."
    masked_ci, placeholders_ci = mask_terms(text, terms, case_sensitive=False)
    restored_ci = unmask_terms(masked_ci, placeholders_ci)
    assert restored_ci == "I ate an Manzana, an Manzana, and an Manzana."

    # Case-sensitive when configured
    masked_cs, placeholders_cs = mask_terms(text, terms, case_sensitive=True)
    restored_cs = unmask_terms(masked_cs, placeholders_cs)
    assert restored_cs == "I ate an apple, an Manzana, and an APPLE."


def test_placeholder_restoration_neural_model_variations():
    placeholders = {
        "LTGLOSSARY0": "inteligencia artificial",
        "LTGLOSSARY1": "aprendizaje automático",
    }

    # Test exact placeholder, brackets, spaces, underscores, case mutations
    mutated_translations = [
        "Me gusta LTGLOSSARY0 y LTGLOSSARY1.",
        "Me gusta LT GLOSSARY 0 y LT GLOSSARY 1.",
        "Me gusta ltglossary0 y ltglossary1.",
        "Me gusta [[LT_GLOSSARY_0]] y [[LT_GLOSSARY_1]].",
        "Me gusta [[LT GLOSSARY 0] y [[LT GLOSSARY 1].",
        "Me gusta [LT _ GLOSSARY _ 0] y [LT _ GLOSSARY _ 1].",
        "Me gusta [ [ LT _ GLOSSARY _ 0 ] ] y [ [ LT _ GLOSSARY _ 1 ] ].",
    ]

    for mutated in mutated_translations:
        restored = unmask_terms(mutated, placeholders)
        assert restored == "Me gusta inteligencia artificial y aprendizaje automático.", f"Failed on: {mutated}"


def test_html_tag_protection():
    terms = {"cat": "gato", "table": "mesa"}
    html_input = '<table class="cat"><tr><td title="cat">The cat is on the table</td></tr></table>'

    masked, placeholders = mask_terms(html_input, terms, is_html=True)
    # Attributes should be untouched
    assert '<table class="cat">' in masked
    assert '<td title="cat">' in masked
    assert "The LTPH" in masked

    restored = unmask_terms(masked, placeholders, is_html=True)
    assert restored == '<table class="cat"><tr><td title="cat">The gato is on the mesa</td></tr></table>'


def test_glossary_class_wrapper():
    engine = Glossary({"hello": "hola", "world": "mundo"})
    text = "hello world!"
    masked, placeholders = engine.mask(text)
    assert "LTPH" in masked
    restored = engine.unmask(masked, placeholders)
    assert restored == "hola mundo!"


def test_merge_glossaries_precedence():
    server_glossary = {
        "device": "aparato",
        "network": "red",
    }
    request_glossary = {
        "device": "dispositivo",  # Overrides server
        "cloud": "nube",
    }
    merged = merge_glossaries(server_glossary, request_glossary)

    assert merged["device"] == "dispositivo"
    assert merged["network"] == "red"
    assert merged["cloud"] == "nube"


def test_validation_success():
    # Valid dict
    res = validate_glossary({"term": "translation"})
    assert res == {"term": "translation"}

    # Valid JSON string
    res2 = validate_glossary('{"term": "translation"}')
    assert res2 == {"term": "translation"}

    # None or empty
    assert validate_glossary(None) == {}
    assert validate_glossary("") == {}
    assert validate_glossary("   ") == {}


def test_validation_errors():
    # Malformed JSON
    with pytest.raises(ValueError, match="Invalid request: glossary must be valid JSON"):
        validate_glossary("{invalid_json")

    # Non-dict
    with pytest.raises(ValueError, match="Invalid request: glossary must be a dictionary"):
        validate_glossary("[1, 2, 3]")

    with pytest.raises(ValueError, match="Invalid request: glossary must be a dictionary"):
        validate_glossary(123)

    # Empty key
    with pytest.raises(ValueError, match="Invalid request: glossary keys must be non-empty strings"):
        validate_glossary({"": "value"})

    with pytest.raises(ValueError, match="Invalid request: glossary keys must be non-empty strings"):
        validate_glossary({"   ": "value"})

    # Empty value
    with pytest.raises(ValueError, match="Invalid request: glossary values must be non-empty strings"):
        validate_glossary({"key": ""})

    # Non-string key or value
    with pytest.raises(ValueError, match="Invalid request: glossary values must be non-empty strings"):
        validate_glossary({"key": 123})

    # Oversized glossary (> 200 entries)
    large_glossary = {f"k{i}": f"v{i}" for i in range(201)}
    with pytest.raises(ValueError, match="exceeds maximum limit of 200 entries"):
        validate_glossary(large_glossary)

    # Oversized key (> 200 chars)
    with pytest.raises(ValueError, match="exceeds 200 characters"):
        validate_glossary({"a" * 201: "val"})

    # Oversized value (> 200 chars)
    with pytest.raises(ValueError, match="exceeds 200 characters"):
        validate_glossary({"key": "v" * 201})


def test_server_glossary_loading_and_fallback():
    with tempfile.TemporaryDirectory() as temp_dir:
        # Write en_es.json
        en_es_file = os.path.join(temp_dir, "en_es.json")
        with open(en_es_file, "w", encoding="utf-8") as f:
            json.dump({"computer": "ordenador", "car": "coche"}, f)

        # Write en-fr.json (with hyphen)
        en_fr_file = os.path.join(temp_dir, "en-fr.json")
        with open(en_fr_file, "w", encoding="utf-8") as f:
            json.dump({"computer": "ordinateur"}, f)

        # Write default.json
        default_file = os.path.join(temp_dir, "default.json")
        with open(default_file, "w", encoding="utf-8") as f:
            json.dump({"global": "global_term", "car": "auto_default"}, f)

        setup(temp_dir)

        # en -> es should have pair terms and default fallback, pair overrides default
        en_es_gloss = get_server_glossary("en", "es")
        assert en_es_gloss["computer"] == "ordenador"
        assert en_es_gloss["car"] == "coche"  # pair takes precedence over default
        assert en_es_gloss["global"] == "global_term"

        # en -> fr should have pair terms and default fallback
        en_fr_gloss = get_server_glossary("en", "fr")
        assert en_fr_gloss["computer"] == "ordinateur"
        assert en_fr_gloss["global"] == "global_term"
        assert en_fr_gloss["car"] == "auto_default"

        # unconfigured pair should get default fallback
        de_it_gloss = get_server_glossary("de", "it")
        assert de_it_gloss["global"] == "global_term"
        assert de_it_gloss["car"] == "auto_default"
        assert "computer" not in de_it_gloss

        # Clean up global state
        setup(None)

