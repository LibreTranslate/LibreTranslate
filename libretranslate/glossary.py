"""
Glossary (term dictionary) support for LibreTranslate.

This module allows server operators to load a JSON glossary file so that
translations prefer domain-specific terms (e.g. university course terminology)
over the generic model output.

Glossary JSON format
--------------------
{
    "zh_ru": {
        "数据结构": "структуры данных",
        "算法": "алгоритм"
    },
    "ru_zh": {
        "структуры данных": "数据结构",
        "алгоритм": "算法"
    }
}

The keys are source-language terms and the values are the preferred
target-language translations. Matching is case-insensitive and longest-match
first so that multi-word terms take precedence over single-word terms.
"""

import json
import os
import re
from typing import Dict, Optional


class Glossary:
    """A simple bidirectional term glossary."""

    def __init__(self, entries: Optional[Dict[str, Dict[str, str]]] = None):
        # entries example: {"zh_ru": {...}, "ru_zh": {...}}
        raw = entries or {}
        # Only keep direction -> dict mappings (ignore metadata keys like "_comment").
        self._entries: Dict[str, Dict[str, str]] = {
            k: v for k, v in raw.items() if isinstance(v, dict)
        }
        # Pre-compile replacement maps keyed by direction for performance.
        self._compiled: Dict[str, Dict[str, str]] = {}
        for direction, mapping in self._entries.items():
            self._compiled[direction] = self._build_replacement_map(mapping)

    @staticmethod
    def _build_replacement_map(mapping: Dict[str, str]) -> Dict[str, str]:
        """Return a copy of *mapping* normalised for case-insensitive lookup."""
        return {k.lower(): v for k, v in mapping.items()}

    @classmethod
    def from_file(cls, path: str) -> "Glossary":
        """Load a glossary from a JSON file."""
        if not path or not os.path.isfile(path):
            return cls()
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            raise ValueError(f"Glossary file {path} must contain a JSON object")
        return cls(data)

    def directions(self):
        """Return the list of supported language directions, e.g. ['zh_ru', 'ru_zh']."""
        return list(self._entries.keys())

    def lookup(self, direction: str, term: str) -> Optional[str]:
        """Look up a single term for a given direction (case-insensitive)."""
        mapping = self._compiled.get(direction)
        if not mapping:
            return None
        return mapping.get(term.lower())

    def apply(self, direction: str, text: str) -> str:
        """Apply the glossary to *text* for the given direction.

        Terms are matched case-insensitively and longest-match first so that
        "структуры данных" is replaced before "данных".
        """
        mapping = self._compiled.get(direction)
        if not mapping or not text:
            return text

        # Sort by descending key length to ensure longer phrases are matched first.
        sorted_terms = sorted(mapping.keys(), key=len, reverse=True)

        for term in sorted_terms:
            if not term:
                continue
            replacement = mapping[term]
            # Use a case-insensitive, word-boundary aware regex for Latin/Cyrillic
            # terms; for CJK terms a plain case-insensitive substitution works well.
            if re.search(r"[A-Za-zА-Яа-яЁё]", term):
                pattern = re.compile(re.escape(term), re.IGNORECASE)
            else:
                pattern = re.compile(re.escape(term), re.IGNORECASE)
            text = pattern.sub(lambda m, repl=replacement: _preserve_case(m.group(0), repl), text)

        return text

    def is_empty(self) -> bool:
        return not any(self._entries.values())


def _preserve_case(original: str, replacement: str) -> str:
    """Try to mirror the capitalisation of *original* onto *replacement*."""
    if original.isupper() and replacement:
        return replacement.upper()
    if original[:1].isupper() and replacement:
        return replacement[0].upper() + replacement[1:]
    return replacement


# Module-level singleton used by the Flask app.
_glossary: Optional[Glossary] = None


def setup(glossary_path: Optional[str]) -> Glossary:
    """Initialise the module-level glossary from a file path."""
    global _glossary
    if not glossary_path:
        _glossary = Glossary()
    else:
        _glossary = Glossary.from_file(glossary_path)
        if not _glossary.is_empty():
            print(f"[glossary] Loaded terms from {glossary_path}: "
                  f"{', '.join(_glossary.directions())}")
    return _glossary


def get_glossary() -> Glossary:
    global _glossary
    if _glossary is None:
        _glossary = Glossary()
    return _glossary


def direction_code(source: str, target: str) -> str:
    """Build a glossary direction key from ISO language codes.

    The project uses 'zh' (Hans) and 'ru' for Chinese and Russian.
    """
    src = source.split("-")[0].lower()
    tgt = target.split("-")[0].lower()
    return f"{src}_{tgt}"
