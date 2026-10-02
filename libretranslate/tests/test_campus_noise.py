import pytest

from libretranslate import campus_noise


class TestProtectRestore:
    def test_protect_course_code(self):
        text = "我选了 CS101 和 МАТ102"
        protected, placeholders = campus_noise.protect(text)
        # Course codes should be replaced with placeholders
        assert "CS101" not in protected
        assert "МАТ102" not in protected
        # Placeholders should map back to originals
        assert "CS101" in placeholders.values()
        assert "МАТ102" in placeholders.values()

    def test_restore_course_code(self):
        text = "我选了 CS101 和 МАТ102"
        protected, placeholders = campus_noise.protect(text)
        restored = campus_noise.restore(protected, placeholders)
        assert "CS101" in restored
        assert "МАТ102" in restored

    def test_protect_abbreviation(self):
        text = "My GPA is 4.0 and I use an IDE"
        protected, placeholders = campus_noise.protect(text)
        assert "GPA" not in protected
        assert "IDE" not in protected
        assert "GPA" in placeholders.values()
        assert "IDE" in placeholders.values()

    def test_restore_abbreviation(self):
        text = "My GPA is 4.0"
        protected, placeholders = campus_noise.protect(text)
        restored = campus_noise.restore(protected, placeholders)
        assert "GPA" in restored

    def test_protect_empty(self):
        text = ""
        protected, placeholders = campus_noise.protect(text)
        assert protected == ""
        assert placeholders == {}

    def test_protect_no_match(self):
        text = "这是一段普通文本，没有课程编号"
        protected, placeholders = campus_noise.protect(text)
        assert protected == text
        assert placeholders == {}

    def test_protect_preserves_text_around(self):
        text = "请在 CS101 课程中使用 SQL"
        protected, placeholders = campus_noise.protect(text)
        restored = campus_noise.restore(protected, placeholders)
        assert restored == text


class TestTransliterateName:
    def test_zh_to_ru_surname(self):
        text = "李老师"
        result = campus_noise.transliterate_name(text, "zh_ru")
        assert "Ли" in result

    def test_zh_to_ru_multiple(self):
        text = "王教授和张同学"
        result = campus_noise.transliterate_name(text, "zh_ru")
        assert "Ван" in result
        assert "Чжан" in result

    def test_ru_to_zh_surname(self):
        text = "Профессор Ли"
        result = campus_noise.transliterate_name(text, "ru_zh")
        assert "李" in result

    def test_ru_to_zh_given_name(self):
        text = "Студент Иван"
        result = campus_noise.transliterate_name(text, "ru_zh")
        assert "伊万" in result

    def test_unknown_direction(self):
        text = "hello"
        assert campus_noise.transliterate_name(text, "en_es") == text


class TestCampusNoiseFilter:
    def test_preprocess_postprocess_roundtrip(self):
        f = campus_noise.CampusNoiseFilter()
        text = "CS101 课程由李教授讲授"
        protected, ph = f.preprocess(text)
        assert "CS101" not in protected
        restored = f.postprocess(protected, ph, "zh_ru")
        assert "CS101" in restored
        assert "Ли" in restored

    def test_disabled_filter(self):
        f = campus_noise.CampusNoiseFilter(enable_protect=False, enable_transliterate=False)
        text = "CS101 课程"
        protected, ph = f.preprocess(text)
        assert protected == text
        assert ph == {}

    def test_protect_only(self):
        f = campus_noise.CampusNoiseFilter(enable_protect=True, enable_transliterate=False)
        text = "CS101 课程"
        protected, ph = f.preprocess(text)
        assert "CS101" not in protected
        restored = f.postprocess(protected, ph, "zh_ru")
        assert "CS101" in restored
        # No transliteration
        assert "课程" in restored


class TestSetup:
    def test_setup_enabled(self):
        f = campus_noise.setup(True)
        assert f.enable_protect is True
        assert f.enable_transliterate is True

    def test_setup_disabled(self):
        f = campus_noise.setup(False)
        assert f.enable_protect is False
        assert f.enable_transliterate is False

    def test_get_filter_default(self):
        campus_noise.setup(False)
        f = campus_noise.get_filter()
        assert f.enable_protect is False
