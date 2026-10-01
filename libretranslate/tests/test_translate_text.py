from libretranslate.app import translate_text


class Hyp:
    def __init__(self, value):
        self.value = value


class FakeTranslator:
    def __init__(self, outputs):
        self.outputs = outputs
        self.calls = []

    def hypotheses(self, text, n):
        self.calls.append(n)
        return [Hyp(o) for o in self.outputs[:n]]


SRC = "Jack of all trades, master of some"
ES = ["Jack de todos los oficios, maestro de algunos", "Jack of all trades, maestro de algunos"]


def test_normal_translation_is_untouched():
    t = FakeTranslator(ES)
    assert translate_text(t, SRC, 1) == (ES[0], [ES[1]])
    assert t.calls == [2]


def test_copy_of_source_is_replaced_with_alternative():
    t = FakeTranslator([SRC] + ES)
    assert translate_text(t, SRC, 2) == (ES[0], [ES[1]])


def test_copy_of_source_without_alternatives_requested():
    t = FakeTranslator([SRC] + ES)
    translated, alternatives = translate_text(t, SRC, 0)
    assert translated == ES[0]
    assert alternatives == []


def test_identical_translation_is_kept_if_nothing_else():
    t = FakeTranslator(["Paris"])
    assert translate_text(t, "Paris", 0) == ("Paris", [])
