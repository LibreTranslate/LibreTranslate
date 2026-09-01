from libretranslate.emoji import (
    contains_emoji,
    detect_translatable,
    mask_emojis_in_html,
    split_emoji_segments,
    translate_preserving_emojis,
    unmask_emojis,
)


def test_detect_translatable_emoji_only():
    assert detect_translatable("🌷🌷🌷") is False
    assert detect_translatable("🌷 🌷") is False
    assert detect_translatable("   ") is False


def test_detect_translatable_mixed_text():
    assert detect_translatable("Hello") is True
    assert detect_translatable("Hello 😆") is True
    assert detect_translatable(["🌷", "Hello"]) is True


def test_contains_emoji():
    assert contains_emoji("Hello") is False
    assert contains_emoji("Hello 😆") is True
    assert contains_emoji("🫠") is True  # Extended-A pictograph


def test_split_emoji_segments_attaches_whitespace():
    segments = split_emoji_segments(
        "Haha, japp, de ligger i min frys. 😆 Gissar på att de kom med Hemglass bilen."
    )
    kinds = [kind for kind, _ in segments]
    texts = [text for _, text in segments]

    assert kinds == ["text", "emoji", "text"]
    assert texts[0] == "Haha, japp, de ligger i min frys."
    assert "😆" in texts[1]
    assert texts[1].startswith(" ")
    assert texts[1].endswith(" ")
    assert texts[2] == "Gissar på att de kom med Hemglass bilen."


def test_split_emoji_segments_zwj_cluster():
    family = "👨‍👩‍👧"
    segments = split_emoji_segments("Hi " + family + " there")
    kinds = [kind for kind, _ in segments]
    assert kinds == ["text", "emoji", "text"]
    assert family in segments[1][1]


def test_split_emoji_segments_no_emoji():
    assert split_emoji_segments("Hello world") == [("text", "Hello world")]


def test_translate_preserving_emojis_does_not_send_emoji_to_model():
    seen = []

    def translate_fn(segment, num_alternatives):
        seen.append(segment)
        assert "😆" not in segment
        return segment.upper(), []

    source = "Haha, japp, de ligger i min frys. 😆 Gissar på att de kom med Hemglass bilen."
    translated, alternatives = translate_preserving_emojis(source, translate_fn, 0)

    assert alternatives == []
    assert "😆" in translated
    assert "HAHA, JAPP, DE LIGGER I MIN FRYS." in translated
    assert "GISSAR PÅ ATT DE KOM MED HEMGLASS BILEN." in translated
    assert seen == [
        "Haha, japp, de ligger i min frys.",
        "Gissar på att de kom med Hemglass bilen.",
    ]


def test_translate_preserving_emojis_passthrough_without_emoji():
    def translate_fn(segment, num_alternatives):
        return "Hola", []

    translated, alternatives = translate_preserving_emojis("Hello", translate_fn, 0)
    assert translated == "Hola"
    assert alternatives == []


def test_translate_preserving_emojis_stitches_alternatives():
    def translate_fn(segment, num_alternatives):
        primary = segment + "-1"
        alts = [segment + "-2"] if num_alternatives else []
        return primary, alts

    translated, alternatives = translate_preserving_emojis("One 😆 Two", translate_fn, 1)
    assert translated == "One-1 😆 Two-1"
    assert alternatives == ["One-2 😆 Two-2"]


def test_mask_and_unmask_emojis_in_html():
    html = "<p>Hello 😆 world</p>"
    masked, tokens = mask_emojis_in_html(html)

    assert "😆" not in masked
    assert "<!--LT_EMOJI_0-->" in masked
    assert tokens == ["😆"]
    assert unmask_emojis(masked, tokens) == html


def test_mask_emojis_in_html_skips_tags():
    html = '<span title="😆">Hi 😊</span>'
    masked, tokens = mask_emojis_in_html(html)

    assert 'title="😆"' in masked
    assert tokens == ["😊"]
    assert unmask_emojis(masked, tokens) == html
