import re

# Rough map of emoji / symbol characters. Space is included so that
# emoji-only (or emoji + whitespace) strings can be skipped by
# detect_translatable() without calling the translation model.
NON_TRANSLATABLE_CODEPOINTS = {e: True for e in \
    [ord(' ')] +                    # Spaces
    list(range(0x1F600, 0x1F64F)) +  # Emoticons
    list(range(0x1F300, 0x1F5FF)) +  # Misc Symbols and Pictographs
    list(range(0x1F680, 0x1F6FF)) +  # Transport and Map
    list(range(0x2600, 0x26FF)) +    # Misc symbols
    list(range(0x2700, 0x27BF)) +    # Dingbats
    list(range(0xFE00, 0xFE0F)) +    # Variation Selectors
    list(range(0x1F900, 0x1F9FF)) +  # Supplemental Symbols and Pictographs
    list(range(0x1F1E6, 0x1F1FF)) +  # Flags
    list(range(0x20D0, 0x20FF))      # Combining Diacritical Marks for Symbols
}

# Additional pictographs used when isolating emojis before translation.
# Keep this broader than NON_TRANSLATABLE_CODEPOINTS so newer emoji
# (and ZWJ sequences) are stripped from model input too.
_EXTRA_EMOJI_RANGES = (
    (0x200D, 0x200D),        # Zero Width Joiner
    (0xFE0F, 0xFE0F),        # Variation Selector-16 (emoji style)
    (0x23E9, 0x23FA),        # Media control pictographs
    (0x2B50, 0x2B50),        # Star
    (0x2B55, 0x2B55),        # Heavy large circle
    (0x1F000, 0x1F02F),      # Mahjong
    (0x1F0A0, 0x1F0FF),      # Playing cards
    (0x1F7E0, 0x1F7FF),      # Colored circles / squares
    (0x1FA00, 0x1FAFF),      # Symbols and Pictographs Extended-A
    (0xE0020, 0xE007F),      # Tags (used in some flag sequences)
)

EMOJI_CODEPOINTS = {cp: True for cp, _ in NON_TRANSLATABLE_CODEPOINTS.items() if cp != ord(' ')}
for start, end in _EXTRA_EMOJI_RANGES:
    for cp in range(start, end + 1):
        EMOJI_CODEPOINTS[cp] = True

_EMOJI_PLACEHOLDER = "<!--LT_EMOJI_{}-->"
_EMOJI_PLACEHOLDER_RE = re.compile(r"<!--LT_EMOJI_(\d+)-->")
_HTML_SPLIT_RE = re.compile(r"(<[^>]*>)")


def is_emoji_char(ch):
    return ord(ch) in EMOJI_CODEPOINTS


def contains_emoji(text):
    return any(is_emoji_char(ch) for ch in text)


def detect_translatable(src_texts):
    if isinstance(src_texts, list):
        return any(detect_translatable(t) for t in src_texts)

    for ch in src_texts:
        if ord(ch) not in NON_TRANSLATABLE_CODEPOINTS:
            return True

    # All emojis / spaces
    return False


def split_emoji_segments(text):
    """Split text into ('text'|'emoji', segment) pairs.

    Adjacent whitespace is attached to emoji clusters so that spacing around
    pictographs is preserved after the surrounding sentences are translated
    independently.
    """
    if not text:
        return []

    n = len(text)
    clusters = []
    i = 0
    while i < n:
        if is_emoji_char(text[i]):
            j = i + 1
            while j < n and is_emoji_char(text[j]):
                j += 1
            clusters.append([i, j])
            i = j
        else:
            i += 1

    if not clusters:
        return [("text", text)]

    for cluster in clusters:
        while cluster[0] > 0 and text[cluster[0] - 1].isspace():
            cluster[0] -= 1
        while cluster[1] < n and text[cluster[1]].isspace():
            cluster[1] += 1

    merged = [clusters[0]]
    for start, end in clusters[1:]:
        if start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])

    segments = []
    pos = 0
    for start, end in merged:
        if pos < start:
            segments.append(("text", text[pos:start]))
        segments.append(("emoji", text[start:end]))
        pos = end
    if pos < n:
        segments.append(("text", text[pos:]))
    return segments


def translate_preserving_emojis(text, translate_fn, num_alternatives=0):
    """Translate text without sending emojis to the model.

    Argos / CTranslate2 models often treat unknown pictograph tokens as the
    end of a sequence, which drops everything after the first emoji
    (https://github.com/LibreTranslate/LibreTranslate/issues/439).

    ``translate_fn(segment, num_alternatives)`` must return
    ``(translated_text, alternatives)``.
    """
    if not contains_emoji(text):
        return translate_fn(text, num_alternatives)

    segments = split_emoji_segments(text)
    primary_parts = []
    alt_parts = []
    max_alts = 0

    for kind, segment in segments:
        if kind == "emoji" or not segment.strip():
            primary_parts.append(segment)
            alt_parts.append(None)
            continue

        translated, alternatives = translate_fn(segment, num_alternatives)
        primary_parts.append(translated)
        alt_parts.append(alternatives)
        max_alts = max(max_alts, len(alternatives))

    translated_text = "".join(primary_parts)
    alternatives = []
    for i in range(max_alts):
        parts = []
        for primary, alts in zip(primary_parts, alt_parts):
            if alts is None or i >= len(alts):
                parts.append(primary)
            else:
                parts.append(alts[i])
        alt = "".join(parts)
        if alt and alt != translated_text:
            alternatives.append(alt)

    return translated_text, alternatives


def mask_emojis_in_html(html):
    """Replace emoji clusters in HTML text nodes with comment placeholders."""
    if not contains_emoji(html):
        return html, []

    tokens = []

    def replace_in_text(chunk):
        if not chunk or not contains_emoji(chunk):
            return chunk

        out = []
        i = 0
        n = len(chunk)
        while i < n:
            if is_emoji_char(chunk[i]):
                j = i + 1
                while j < n and is_emoji_char(chunk[j]):
                    j += 1
                tokens.append(chunk[i:j])
                out.append(_EMOJI_PLACEHOLDER.format(len(tokens) - 1))
                i = j
            else:
                out.append(chunk[i])
                i += 1
        return "".join(out)

    parts = _HTML_SPLIT_RE.split(html)
    masked = []
    for part in parts:
        if part.startswith("<") and part.endswith(">"):
            masked.append(part)
        else:
            masked.append(replace_in_text(part))
    return "".join(masked), tokens


def unmask_emojis(text, tokens):
    if not tokens:
        return text

    def repl(match):
        idx = int(match.group(1))
        if 0 <= idx < len(tokens):
            return tokens[idx]
        return match.group(0)

    return _EMOJI_PLACEHOLDER_RE.sub(repl, text)
