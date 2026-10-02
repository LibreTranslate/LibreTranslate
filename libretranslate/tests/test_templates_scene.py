import os

import pytest

from libretranslate import templates_scene


@pytest.fixture(autouse=True)
def _reset_manager():
    templates_scene.setup()
    yield


class TestSceneTemplate:
    def test_render_with_all_variables(self):
        data = {
            "name": {"zh": "测试", "ru": "Тест"},
            "description": {"zh": "", "ru": ""},
            "variables": ["course", "date"],
            "zh": "课程：{course}，日期：{date}",
            "ru": "Курс: {course}, дата: {date}",
        }
        t = templates_scene.SceneTemplate("test", data)
        result = t.render({"course": "数据结构", "date": "2024-01-01"})
        assert result["zh"] == "课程：数据结构，日期：2024-01-01"
        assert result["ru"] == "Курс: 数据结构, дата: 2024-01-01"

    def test_render_with_missing_variable(self):
        data = {
            "name": {"zh": "测试", "ru": "Тест"},
            "variables": ["course"],
            "zh": "课程：{course}",
            "ru": "Курс: {course}",
        }
        t = templates_scene.SceneTemplate("test", data)
        # Missing variable should become empty string
        result = t.render({})
        assert result["zh"] == "课程："
        assert result["ru"] == "Курс: "

    def test_to_dict(self):
        data = {
            "name": {"zh": "测试", "ru": "Тест"},
            "description": {"zh": "描述", "ru": "Описание"},
            "variables": ["course"],
            "zh": "",
            "ru": "",
        }
        t = templates_scene.SceneTemplate("test", data)
        d = t.to_dict()
        assert d["id"] == "test"
        assert d["name"]["zh"] == "测试"
        assert d["variables"] == ["course"]


class TestTemplateManager:
    def test_load_default_templates(self):
        manager = templates_scene.TemplateManager()
        assert manager.count() > 0
        templates = manager.list_templates()
        ids = [t["id"] for t in templates]
        assert "class_notification" in ids
        assert "exam_notification" in ids

    def test_render_known_template(self):
        manager = templates_scene.TemplateManager()
        result = manager.render("class_notification", {
            "course": "数据结构",
            "date": "2024-01-15",
            "time": "10:00",
            "location": "A301",
            "reason": "教室调整",
        })
        assert "数据结构" in result["zh"]
        assert "数据结构" in result["ru"]
        assert "A301" in result["zh"]

    def test_get_unknown_template_raises(self):
        manager = templates_scene.TemplateManager()
        with pytest.raises(templates_scene.TemplateNotFoundError):
            manager.get("nonexistent")

    def test_load_from_nonexistent_file(self):
        manager = templates_scene.TemplateManager("/nonexistent/path.json")
        assert manager.count() == 0


class TestFormatFunction:
    def test_replace_placeholder(self):
        assert templates_scene._format("Hello {name}", {"name": "World"}) == "Hello World"

    def test_missing_placeholder_kept(self):
        assert templates_scene._format("Hello {name}", {}) == "Hello {name}"

    def test_multiple_placeholders(self):
        assert templates_scene._format("{a} {b}", {"a": "1", "b": "2"}) == "1 2"
