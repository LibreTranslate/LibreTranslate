import json
import re
from html import unescape

from libretranslate.language import improve_translation_formatting

MAX_WORDS = 200
MAX_WORD_LENGTH = 200
RETRY_HYPOTHESES = 4
NO_WORD_BOUNDARIES = ("zh", "zt", "ja", "ko", "th")
PLACEHOLDER = re.compile(r"V(\d{1,4})Z", re.IGNORECASE)


def parse_glossary(raw):
    if raw is None or raw == "":
        return {}

    if isinstance(raw, str):
        raw = json.loads(raw)

    if not isinstance(raw, dict) or len(raw) > MAX_WORDS:
        raise ValueError("Invalid glossary")

    words = {}
    for source, target in raw.items():
        if not isinstance(target, str):
            raise ValueError("Invalid glossary")

        source, target = source.strip(), target.strip()
        if not source or not target or max(len(source), len(target)) > MAX_WORD_LENGTH:
            raise ValueError("Invalid glossary")

        words[source] = target

    return words


class GlossaryTranslator:
    def __init__(self, translator, words):
        self.translator = translator
        self.to_lang = translator.to_lang

        sources = sorted(words, key=len, reverse=True)
        self.targets = [words[s] for s in sources]

        pattern = "|".join(f"({re.escape(s)})" for s in sources)
        if translator.from_lang.code not in NO_WORD_BOUNDARIES:
            pattern = rf"(?<!\w)(?:{pattern})(?!\w)"
        self.pattern = re.compile(pattern, re.IGNORECASE)

    def translate(self, text):
        return "\n".join(self.translate_line(line, 1, False)[0] for line in text.split("\n"))

    def hypotheses(self, text, num_hypotheses):
        lines = [self.translate_line(line, num_hypotheses, True) for line in text.split("\n")]
        count = max(len(line) for line in lines)
        return ["\n".join(line[min(i, len(line) - 1)] for line in lines) for i in range(count)]

    def translate_line(self, line, num_hypotheses, improve):
        if not line.strip():
            return [line]

        found = []

        def mask(match):
            found.append(self.targets[match.lastindex - 1])
            return f"V{len(found) - 1}Z"

        masked = self.pattern.sub(mask, line)
        if len(found) == 1 and masked.strip() == "V0Z":
            return [masked.replace("V0Z", found[0])]
        
        if found:
            results = self.run_masked(masked, line, found, num_hypotheses, improve)
            
            # Sometimes we retry because models sometimes break placeholders
            if not results and num_hypotheses < RETRY_HYPOTHESES:
                results = self.run_masked(masked, line, found, RETRY_HYPOTHESES, improve)
            if results:
                return results[:num_hypotheses]

        return self.run(line, line, num_hypotheses, improve)

    def run_masked(self, masked, source, found, count, improve):
        results = []
        for text in self.run(masked, source, count, improve):
            indexes = [int(i) for i in PLACEHOLDER.findall(text)]
            if sorted(indexes) == list(range(len(found))):
                results.append(PLACEHOLDER.sub(lambda m: found[int(m.group(1))], text))
        return results

    def run(self, text, source, count, improve):
        results = [h.value for h in self.translator.hypotheses(text, count)]
        if improve:
            results = [unescape(improve_translation_formatting(source, r)) for r in results]
        return results
