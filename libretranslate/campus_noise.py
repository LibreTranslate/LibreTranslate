"""
Campus "noise" filter for LibreTranslate.

University texts contain many tokens that generic translation models mishandle:
course codes (CS101, МАТ102), abbreviations (GPA, GPA->Средний балл), and
personal names that need transliteration rather than translation.

This module provides:
  * protect(text) -> (text, placeholders)
      Replace course codes and known abbreviations with unique placeholders
      so the translation engine leaves them alone.
  * restore(text, placeholders) -> text
      Put the original tokens back after translation.
  * transliterate_name(text, direction) -> text
      Transliterate personal names between Latin/Cyrillic and Chinese using a
      seed name table.

The module is intentionally dependency-free and can be unit-tested in
isolation.
"""

import re
import uuid
from typing import Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Course code patterns
# ---------------------------------------------------------------------------
# e.g. CS101, CS-101, МАТ102, ИВТ-201, М301, CSE201a
_COURSE_CODE_RE = re.compile(
    r"\b(?:[A-ZА-ЯЁ]{1,6}[-\s]?\d{2,4}[A-Za-zА-Яа-яЁё]?)\b"
)

# Common campus abbreviations that should be kept verbatim or expanded.
# Keys are matched case-insensitively.
_ABBREVIATIONS = {
    # Degree / academic
    "GPA": "GPA",
    "gpa": "GPA",
    "PhD": "PhD",
    "phd": "PhD",
    "BSc": "BSc",
    "bsc": "BSc",
    "MSc": "MSc",
    "msc": "MSc",
    "BA": "BA",
    "ma": "MA",
    "MA": "MA",
    # University common
    "URL": "URL",
    "URLs": "URLs",
    "API": "API",
    "CPU": "CPU",
    "GPU": "GPU",
    "RAM": "RAM",
    "ROM": "ROM",
    "IP": "IP",
    "OS": "OS",
    "DB": "DB",
    "DBMS": "DBMS",
    "SQL": "SQL",
    "HTTP": "HTTP",
    "HTTPS": "HTTPS",
    "HTML": "HTML",
    "CSS": "CSS",
    "JSON": "JSON",
    "XML": "XML",
    "IDE": "IDE",
    "SDK": "SDK",
    "GUI": "GUI",
    "CLI": "CLI",
    "AI": "AI",
    "ML": "ML",
    "DL": "DL",
    "NN": "NN",
    "NLP": "NLP",
    "CV": "CV",
    "IoT": "IoT",
    "UI": "UI",
    "UX": "UX",
    "IT": "IT",
    "ICT": "ICT",
    # Time
    "AM": "AM",
    "PM": "PM",
}

# Build a case-insensitive lookup but preserve original casing on output.
def _build_abbrev_set() -> set:
    return {k.lower() for k in _ABBREVIATIONS}

_ABBREV_SET = _build_abbrev_set()


# ---------------------------------------------------------------------------
# Name transliteration tables (zh <-> ru/latin)
# ---------------------------------------------------------------------------
# A small seed table of common Russian and Chinese personal names.
_ZH_TO_RU_NAMES = {
    "李": "Ли",
    "王": "Ван",
    "张": "Чжан",
    "刘": "Лю",
    "陈": "Чэнь",
    "杨": "Ян",
    "赵": "Чжао",
    "黄": "Хуан",
    "周": "Чжоу",
    "吴": "У",
    "徐": "Сюй",
    "孙": "Сунь",
    "马": "Ма",
    "朱": "Чжу",
    "胡": "Ху",
    "郭": "Го",
    "何": "Хэ",
    "高": "Гао",
    "林": "Линь",
    "罗": "Ло",
    "郑": "Чжэн",
    "梁": "Лян",
    "谢": "Се",
    "宋": "Сун",
    "唐": "Тан",
    "韩": "Хань",
    "冯": "Фэн",
    "于": "Юй",
    "董": "Дун",
    "萧": "Сяо",
}

_RU_TO_ZH_NAMES = {v: k for k, v in _ZH_TO_RU_NAMES.items()}

# Common Russian given names -> Chinese
_RU_GIVEN_TO_ZH = {
    "Иван": "伊万",
    "Пётр": "彼得",
    "Петр": "彼得",
    "Александр": "亚历山大",
    "Дмитрий": "德米特里",
    "Сергей": "谢尔盖",
    "Андрей": "安德烈",
    "Михаил": "米哈伊尔",
    "Николай": "尼古拉",
    "Владимир": "弗拉基米尔",
    "Елена": "叶莲娜",
    "Анна": "安娜",
    "Мария": "玛丽亚",
    "Ольга": "奥尔加",
    "Татьяна": "塔季扬娜",
    "Светлана": "斯维特拉娜",
    "Наталья": "纳塔利娅",
    "Екатерина": "叶卡捷琳娜",
}

_ZH_GIVEN_TO_RU = {v: k for k, v in _RU_GIVEN_TO_ZH.items()}


def _placeholder() -> str:
    """Return a unique placeholder token unlikely to collide with real text."""
    return "\x00PH" + uuid.uuid4().hex[:8] + "\x00"


def protect(text: str) -> Tuple[str, Dict[str, str]]:
    """Replace course codes and abbreviations with placeholders.

    Returns (protected_text, placeholders) where placeholders maps
    placeholder -> original token.
    """
    placeholders: Dict[str, str] = {}

    def _replace_course(match):
        token = match.group(0)
        ph = _placeholder()
        placeholders[ph] = token
        return ph

    text = _COURSE_CODE_RE.sub(_replace_course, text)

    # Protect abbreviations (whole word match, case-insensitive).
    def _replace_abbrev(match):
        token = match.group(0)
        if token.lower() in _ABBREV_SET:
            ph = _placeholder()
            placeholders[ph] = token
            return ph
        return token

    text = re.sub(r"\b[A-Za-zА-Яа-яЁё]{1,8}\b", _replace_abbrev, text)

    return text, placeholders


def restore(text: str, placeholders: Dict[str, str]) -> str:
    """Replace placeholders with their original tokens."""
    for ph, original in placeholders.items():
        text = text.replace(ph, original)
    return text


def transliterate_name(text: str, direction: str) -> str:
    """Transliterate personal names in *text*.

    direction: 'zh_ru' or 'ru_zh'.
    Only known names from the seed tables are converted; everything else
    is left unchanged.
    """
    if direction == "zh_ru":
        return _transliterate_zh_ru(text)
    elif direction == "ru_zh":
        return _transliterate_ru_zh(text)
    return text


def _transliterate_zh_ru(text: str) -> str:
    # Surnames (single Chinese character) first — longest is one char here.
    for zh, ru in _ZH_TO_RU_NAMES.items():
        text = text.replace(zh, ru)
    # Given names.
    for zh, ru in _ZH_GIVEN_TO_RU.items():
        text = text.replace(zh, ru)
    return text


def _transliterate_ru_zh(text: str) -> str:
    # Replace longer tokens first to avoid partial matches.
    for ru, zh in sorted(_RU_TO_ZH_NAMES.items(), key=lambda x: -len(x[0])):
        text = text.replace(ru, zh)
    for ru, zh in sorted(_RU_GIVEN_TO_ZH.items(), key=lambda x: -len(x[0])):
        text = text.replace(ru, zh)
    return text


class CampusNoiseFilter:
    """Convenience wrapper combining protect/restore/transliterate."""

    def __init__(self, enable_protect: bool = True, enable_transliterate: bool = True):
        self.enable_protect = enable_protect
        self.enable_transliterate = enable_transliterate

    def preprocess(self, text: str) -> Tuple[str, Dict[str, str]]:
        if self.enable_protect:
            return protect(text)
        return text, {}

    def postprocess(self, text: str, placeholders: Dict[str, str], direction: str = "") -> str:
        text = restore(text, placeholders)
        if self.enable_transliterate and direction:
            text = transliterate_name(text, direction)
        return text


# Module-level singleton.
_filter: Optional[CampusNoiseFilter] = None


def setup(enabled: bool) -> CampusNoiseFilter:
    global _filter
    _filter = CampusNoiseFilter(enable_protect=enabled, enable_transliterate=enabled)
    return _filter


def get_filter() -> CampusNoiseFilter:
    global _filter
    if _filter is None:
        _filter = CampusNoiseFilter(enable_protect=False, enable_transliterate=False)
    return _filter
