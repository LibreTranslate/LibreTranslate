import json
import os
import re
from typing import Any, Dict, List, Optional, Tuple

MAX_GLOSSARY_ENTRIES = 200
MAX_TERM_LENGTH = 200

# Server-side loaded glossaries:
# Keys are either a tuple of (source_lang, target_lang) in lowercase or 'default'
_server_glossaries: Dict[Any, Dict[str, str]] = {}


def validate_glossary(glossary_input: Any) -> Dict[str, str]:
    """Validate and normalize a glossary input.

    Accepts a dictionary or a JSON-encoded string.
    Ensures keys and values are non-empty strings, enforces limits,
    and returns a clean Dict[str, str].
    Raises ValueError with a user-friendly error message on invalid input.
    """
    if glossary_input is None:
        return {}

    parsed = glossary_input
    if isinstance(glossary_input, str):
        trimmed = glossary_input.strip()
        if not trimmed:
            return {}
        try:
            parsed = json.loads(trimmed)
        except (json.JSONDecodeError, ValueError):
            raise ValueError("Invalid request: glossary must be valid JSON")

    if not isinstance(parsed, dict):
        raise ValueError("Invalid request: glossary must be a dictionary")

    if len(parsed) > MAX_GLOSSARY_ENTRIES:
        raise ValueError(
            f"Invalid request: glossary exceeds maximum limit of {MAX_GLOSSARY_ENTRIES} entries"
        )

    validated: Dict[str, str] = {}
    for key, value in parsed.items():
        if not isinstance(key, str) or not key.strip():
            raise ValueError("Invalid request: glossary keys must be non-empty strings")
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Invalid request: glossary values must be non-empty strings")
        if len(key) > MAX_TERM_LENGTH:
            raise ValueError(
                f"Invalid request: glossary key '{key}' exceeds {MAX_TERM_LENGTH} characters"
            )
        if len(value) > MAX_TERM_LENGTH:
            raise ValueError(
                f"Invalid request: glossary value for '{key}' exceeds {MAX_TERM_LENGTH} characters"
            )
        validated[key] = value

    return validated


def load_server_glossaries(glossaries_dir: Optional[str]) -> Dict[Any, Dict[str, str]]:
    """Load JSON glossary files from a directory.

    Supports language-pair filenames (e.g. en_es.json, en-es.json)
    containing {"source_term": "target_term"} mappings, plus an optional default.json fallback.
    """
    glossaries: Dict[Any, Dict[str, str]] = {}

    if not glossaries_dir or not os.path.isdir(glossaries_dir):
        return glossaries

    try:
        filenames = os.listdir(glossaries_dir)
    except OSError as e:
        print(f"Failed to read glossaries directory {glossaries_dir}: {e}")
        return glossaries

    for filename in sorted(filenames):
        if not filename.lower().endswith(".json"):
            continue

        base_name = os.path.splitext(filename)[0].lower()
        filepath = os.path.join(glossaries_dir, filename)

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f"Failed to parse glossary file {filepath}: {e}")
            continue

        try:
            validated = validate_glossary(data)
        except ValueError as e:
            print(f"Skipping invalid glossary file {filepath}: {e}")
            continue

        if base_name == "default":
            glossaries["default"] = validated
            print(f"Loaded default server glossary with {len(validated)} terms from {filename}")
        elif "_" in base_name:
            src, tgt = base_name.split("_", 1)
            glossaries[(src.strip(), tgt.strip())] = validated
            print(f"Loaded server glossary for {src}->{tgt} with {len(validated)} terms from {filename}")
        elif "-" in base_name:
            src, tgt = base_name.split("-", 1)
            glossaries[(src.strip(), tgt.strip())] = validated
            print(f"Loaded server glossary for {src}->{tgt} with {len(validated)} terms from {filename}")
        else:
            print(f"Glossary filename {filename} does not match expected pattern (lang_lang.json or default.json)")

    return glossaries


def setup(glossaries_dir: Optional[str] = None) -> None:
    """Initialize server-side glossaries from the configured directory."""
    global _server_glossaries
    _server_glossaries = load_server_glossaries(glossaries_dir)


def get_server_glossary(source_lang: Optional[str], target_lang: Optional[str]) -> Dict[str, str]:
    """Retrieve the server-side glossary for a language pair, falling back to default.json."""
    result: Dict[str, str] = {}

    # Start with default fallback if present
    if "default" in _server_glossaries:
        result.update(_server_glossaries["default"])

    if source_lang and target_lang:
        src = source_lang.lower().strip()
        tgt = target_lang.lower().strip()
        pair_key = (src, tgt)
        if pair_key in _server_glossaries:
            # Pair-specific glossary overrides default fallback
            result.update(_server_glossaries[pair_key])

    return result


def merge_glossaries(
    server_glossary: Optional[Dict[str, str]],
    request_glossary: Optional[Dict[str, str]],
) -> Dict[str, str]:
    """Merge server-side and request-level glossaries.

    Request-level terms take precedence over server-side terms.
    """
    merged: Dict[str, str] = {}
    if server_glossary:
        merged.update(server_glossary)
    if request_glossary:
        merged.update(request_glossary)
    return merged


def _build_term_pattern(term: str) -> str:
    """Build a regex pattern for a single term with boundary awareness where applicable."""
    escaped = re.escape(term)
    prefix = r"\b" if re.match(r"^\w", term) else ""
    suffix = r"\b" if re.search(r"\w$", term) else ""
    return f"{prefix}{escaped}{suffix}"


def _get_restore_pattern(placeholder: str) -> re.Pattern:
    """Build a flexible regex pattern to match a placeholder even with neural model mutations."""
    # Look for numeric index in placeholder, e.g. LTPH0, LTGLOSSARY0 or [[LT_GLOSSARY_0]]
    num_match = re.search(r"(\d+)", placeholder)
    if num_match:
        idx = num_match.group(1)
        # Matches LTPH{idx}, LTTOK{idx}, LTGLOSSARY{idx}, LTGLOSARIO{idx}, [[LT_GLOSSARY_{idx}]], etc.
        pattern_str = (
            rf"(?:\[\s*\[\s*|\[\s*)?"
            rf"LT\s*[_ ]?\s*(?:GLOSSARY|GLOSARIO|PH|TOK)?\s*[_ ]?\s*{idx}(?!\d)"
            rf"(?:\s*\]\s*\]|\s*\])?"
        )
        return re.compile(pattern_str, re.IGNORECASE)
    # Fallback to escaped placeholder
    return re.compile(re.escape(placeholder))


def mask_text_terms(
    text: str,
    glossary: Dict[str, str],
    case_sensitive: bool = False,
    placeholder_prefix: str = "LTPH",
) -> Tuple[str, Dict[str, str]]:
    """Replace matched source terms in plain text with model-safe placeholders."""
    if not text or not glossary:
        return text, {}

    # Sort source terms by character length descending so multi-word phrases match first
    sorted_terms = sorted(glossary.keys(), key=lambda t: len(t), reverse=True)

    # Map each term to a placeholder
    term_to_placeholder: Dict[str, str] = {}
    placeholder_map: Dict[str, str] = {}
    patterns: List[str] = []

    for i, term in enumerate(sorted_terms):
        placeholder = f"{placeholder_prefix}{i}"
        term_to_placeholder[term] = placeholder
        placeholder_map[placeholder] = glossary[term]
        patterns.append(f"(?P<T{i}>{_build_term_pattern(term)})")

    flags = 0 if case_sensitive else re.IGNORECASE
    combined_regex = re.compile("|".join(patterns), flags)

    matched_placeholders: Dict[str, str] = {}

    def _replace_match(match: re.Match) -> str:
        for group_name, matched_value in match.groupdict().items():
            if matched_value is not None:
                idx = int(group_name[1:])
                term = sorted_terms[idx]
                placeholder = term_to_placeholder[term]
                matched_placeholders[placeholder] = placeholder_map[placeholder]
                return placeholder
        return match.group(0)

    masked_text = combined_regex.sub(_replace_match, text)
    return masked_text, matched_placeholders


def unmask_text_terms(text: str, placeholder_map: Dict[str, str]) -> str:
    """Restore placeholders in plain text with their exact target terms."""
    if not text or not placeholder_map:
        return text

    restored = text
    # Sort placeholders by index descending to avoid substring collision (e.g. 10 before 1)
    sorted_placeholders = sorted(
        placeholder_map.keys(),
        key=lambda p: int(re.search(r"(\d+)", p).group(1)) if re.search(r"(\d+)", p) else len(p),
        reverse=True,
    )

    for placeholder in sorted_placeholders:
        target_term = placeholder_map[placeholder]
        pattern = _get_restore_pattern(placeholder)
        restored = pattern.sub(lambda _: target_term, restored)

    return restored


def mask_terms(
    text: str,
    glossary: Dict[str, str],
    case_sensitive: bool = False,
    is_html: bool = False,
    placeholder_prefix: str = "LTPH",
) -> Tuple[str, Dict[str, str]]:
    """Mask glossary terms in text or HTML markup.

    When is_html=True, only text content outside HTML tags is modified.
    """
    if not text or not glossary:
        return text, {}

    if not is_html:
        return mask_text_terms(
            text,
            glossary,
            case_sensitive=case_sensitive,
            placeholder_prefix=placeholder_prefix,
        )

    # HTML handling: tokenize by HTML tags to isolate text nodes
    parts = re.split(r"(<[^>]+>)", text)
    all_placeholders: Dict[str, str] = {}
    masked_parts: List[str] = []

    for part in parts:
        if part.startswith("<") and part.endswith(">"):
            # HTML tag, keep untouched
            masked_parts.append(part)
        elif part:
            # Text node, mask glossary terms
            masked_part, placeholders = mask_text_terms(
                part,
                glossary,
                case_sensitive=case_sensitive,
                placeholder_prefix=placeholder_prefix,
            )
            masked_parts.append(masked_part)
            all_placeholders.update(placeholders)
        else:
            masked_parts.append(part)

    return "".join(masked_parts), all_placeholders


def unmask_terms(
    text: str,
    placeholder_map: Dict[str, str],
    is_html: bool = False,
) -> str:
    """Unmask placeholders in text or HTML markup, restoring exact target terms."""
    if not text or not placeholder_map:
        return text

    if not is_html:
        return unmask_text_terms(text, placeholder_map)

    # HTML handling: only unmask text nodes outside HTML tags
    parts = re.split(r"(<[^>]+>)", text)
    restored_parts: List[str] = []

    for part in parts:
        if part.startswith("<") and part.endswith(">"):
            restored_parts.append(part)
        elif part:
            restored_parts.append(unmask_text_terms(part, placeholder_map))
        else:
            restored_parts.append(part)

    return "".join(restored_parts)


class Glossary:
    """High-level class for managing and applying a terminology glossary."""

    def __init__(self, entries: Optional[Dict[str, str]] = None, case_sensitive: bool = False):
        self.entries: Dict[str, str] = entries or {}
        self.case_sensitive: bool = case_sensitive

    def mask(self, text: str, is_html: bool = False) -> Tuple[str, Dict[str, str]]:
        return mask_terms(text, self.entries, case_sensitive=self.case_sensitive, is_html=is_html)

    def unmask(self, text: str, placeholder_map: Dict[str, str], is_html: bool = False) -> str:
        return unmask_terms(text, placeholder_map, is_html=is_html)

