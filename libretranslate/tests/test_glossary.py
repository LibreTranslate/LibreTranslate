import os
import sys

import pytest

from libretranslate import glossary


@pytest.fixture
def sample_glossary():
    return glossary.Glossary({
        "zh_ru": {
            "数据结构": "структуры данных",
            "算法": "алгоритм",
            "深圳北理莫斯科大学": "Университет МГУ-ППИ в Шэньчжэне",
        },
        "ru_zh": {
            "структуры данных": "数据结构",
            "алгоритм": "算法",
            "Университет МГУ-ППИ в Шэньчжэне": "深圳北理莫斯科大学",
        },
    })


class TestGlossary:
    def test_lookup_case_insensitive(self, sample_glossary):
        assert sample_glossary.lookup("zh_ru", "数据结构") == "структуры данных"
        assert sample_glossary.lookup("ru_zh", "Алгоритм") == "算法"

    def test_lookup_missing(self, sample_glossary):
        assert sample_glossary.lookup("zh_ru", "不存在的词") is None
        assert sample_glossary.lookup("en_es", "hello") is None

    def test_apply_single_term(self, sample_glossary):
        text = "我正在学习数据结构"
        result = sample_glossary.apply("zh_ru", text)
        assert "структуры данных" in result
        assert "数据结构" not in result

    def test_apply_ru_to_zh(self, sample_glossary):
        text = "Я изучаю структуры данных"
        result = sample_glossary.apply("ru_zh", text)
        assert "数据结构" in result
        assert "структуры данных" not in result

    def test_apply_empty_direction(self, sample_glossary):
        text = "hello world"
        assert sample_glossary.apply("en_es", text) == text

    def test_apply_empty_text(self, sample_glossary):
        assert sample_glossary.apply("zh_ru", "") == ""

    def test_apply_longest_match_first(self):
        g = glossary.Glossary({
            "zh_ru": {
                "数据库系统": "системы баз данных",
                "数据库": "базы данных",
            }
        })
        text = "数据库系统很重要"
        result = g.apply("zh_ru", text)
        assert "системы баз данных" in result
        assert "базы данных" not in result.split("системы баз данных")[0]

    def test_is_empty(self):
        g = glossary.Glossary()
        assert g.is_empty() is True

        g2 = glossary.Glossary({"zh_ru": {"a": "b"}})
        assert g2.is_empty() is False

    def test_directions(self, sample_glossary):
        assert set(sample_glossary.directions()) == {"zh_ru", "ru_zh"}


class TestGlossaryFromFile:
    def test_from_file_not_found(self):
        g = glossary.Glossary.from_file("/nonexistent/path.json")
        assert g.is_empty()

    def test_from_file_empty_path(self):
        g = glossary.Glossary.from_file("")
        assert g.is_empty()

    def test_from_file_valid(self, tmp_path):
        path = tmp_path / "g.json"
        path.write_text('{"zh_ru": {"测试": "тест"}}', encoding="utf-8")
        g = glossary.Glossary.from_file(str(path))
        assert g.lookup("zh_ru", "测试") == "тест"


class TestDirectionCode:
    def test_simple(self):
        assert glossary.direction_code("zh", "ru") == "zh_ru"
        assert glossary.direction_code("ru", "zh") == "ru_zh"

    def test_with_variant(self):
        # zh-Hans should map to zh
        assert glossary.direction_code("zh-Hans", "ru") == "zh_ru"
