# Originally adapted from https://github.com/aboSamoor/polyglot/blob/master/polyglot/base.py

from abc import ABC

import lingua
import pycld2 as cld2

class UnknownLanguage(Exception):
    pass


class Language(object):
    def __init__(self, choice: "tuple[str, str, float | int, int]") -> None:
        name, code, confidence, bytesize = choice
        self.code = code
        self.name = name
        self.confidence = float(confidence)
        self.read_bytes = int(bytesize)

    def __str__(self) -> str:
        return "name: {:<12}code: {:<9}confidence: {:>5.1f} " "read bytes:{:>6}".format(
            self.name, self.code, self.confidence, self.read_bytes
        )

    def __repr__(self) -> str:
        return "Language((%r, %r, %r, %r))" % (
            self.name, self.code, self.confidence, self.read_bytes
        )

    def to_dict(self, confidence_digits: int = 2) -> "dict[str, str | int]":
        return {
            "confidence": round(self.confidence, confidence_digits),
            "language": self.code.lower()
        }

    @staticmethod
    def from_code(code: str) -> "Language":
        return Language(("", code, 100, 0))


class BaseDetector(ABC):
    """Detect the language used in a snippet of text."""

    def __init__(
        self,
        text: str,
        quiet: bool = False,
        allowed_languages: "Iterable[str] | None" = None,
    ) -> None:
        """Detector of the language used in `text`.
        Args:
          text (string): unicode string.
        """
        self.allowed_languages: "frozenset[str]" = frozenset(
            self.supported_languages()
            if allowed_languages is None
            else [string.upper() for string in allowed_languages]
        )
        # self.__text = text
        self.reliable: bool = True
        """False if the detector used Best Effort strategy in detection."""
        self.quiet: bool = quiet
        """If true, exceptions will be silenced."""
        self.languages: "list[Language]" = [
            lang
            for lang in self.detect(text)
            if lang.code.upper() in self.allowed_languages
        ]
        self.language: "Language | None" = self.languages[0] if self.languages else None

    def __str__(self) -> str:
        text = "Prediction is reliable: {}\n".format(self.reliable)
        text += "\n".join(
            [
                "Language {}: {}".format(i + 1, str(l))
                for i, l in enumerate(self.languages)
            ]
        )
        return text

    @classmethod
    def supported_languages(cls) -> "list[str]":
        """Returns a list of the languages that this Detector can detect."""
        raise NotImplementedError()

    def detect(self, text: str) -> "list[Language]":
        """Decide which language is used to write the text."""
        raise NotImplementedError()


class Cld2Detector(BaseDetector):
    """Detect the language used in a snippet of text."""

    @classmethod
    def supported_languages(cls) -> "list[str]":
        """Returns a list of the languages that can be detected by pycld2."""
        return [
            name.capitalize()
            for name, code in cld2.LANGUAGES
            if not name.startswith("X_")
        ]

    def detect(self, text: str) -> "list[Language]":
        """Decide which language is used to write the text.
        The method tries first to detect the language with high reliability. If
        that is not possible, the method switches to the best effort strategy.
        Args:
          text (string): A snippet of text, the longer it is the more reliable we
                         can detect the language used to write the text.
        """
        reliable, index, top_3_choices = cld2.detect(text, bestEffort=False)

        if not reliable:
            self.reliable = False
            reliable, index, _top_3_choices = cld2.detect(text, bestEffort=True)
            if not self.quiet:
                if not reliable:
                    raise UnknownLanguage("Try passing a longer snippet of text")
            top_3_choices = _top_3_choices
        return [Language(x) for x in top_3_choices if x[0] != "Unknown"]


class LinguaDetector(BaseDetector):
    """Detect the language used in a snippet of text."""

    @classmethod
    def supported_languages(cls) -> "list[str]":
        """Returns a list of the languages that can be detected by pycld2."""
        return [
            lang.iso_code_639_1.name
            for lang in lingua.Language.all()
        ]

    def detect(self, text: str) -> "list[Language]":
        """Decide which language is used to write the text.
        Args:
          text (string): A snippet of text, the longer it is the more reliable we
                         can detect the language used to write the text.
        """
        languages = [
            lingua.Language.from_iso_code_639_1(lingua.IsoCode639_1[lang])
            for lang in self.allowed_languages
        ]
        detector = lingua.LanguageDetectorBuilder.from_languages(*languages).build()
        confidence_values: "list[tuple[lingua.Language, float]]" = detector.compute_language_confidence_values(text)
        filter_no_confidence = max(c for _, c in confidence_values) > 0
        return [
            Language((language.name.title(), language.iso_code_639_1.name, confidence * 100.0, len(text)))
            for language, confidence in confidence_values
            if not filter_no_confidence or confidence
        ]


class Detector(BaseDetector):
    @classmethod
    def detectors(cls) -> "tuple[type[BaseDetector], ...]":
        return Cld2Detector, LinguaDetector

    @classmethod
    def supported_languages(cls) -> "list[str]":
        """Returns a list of the languages that this Detector can detect."""
        languages = set()
        for detector in cls.detectors():
            languages.update(detector.supported_languages())
        return list(languages)

    def detect(self, text: str) -> "list[Language]":
        """Decide which language is used to write the text."""
        languages = []
        failed = 0
        for detector in self.detectors():
            try:
                languages.extend(
                    detector(
                        text,
                        quiet=self.quiet,
                        allowed_languages=self.allowed_languages,
                    ).languages
                )
            except UnknownLanguage:
                failed += 1
        if not self.quiet and failed == len(self.detectors()):
            raise UnknownLanguage("Try passing a longer snippet of text")
        languages.sort(key=lambda l: l.confidence, reverse=True)
        print(languages)
        return languages


def test_Detector():
    for lang in Detector.supported_languages():
        assert len(lang) == 2 and lang.upper() == lang, lang
    assert Detector("Neuland").language.code == "DE"
    # https://github.com/LibreTranslate/LibreTranslate/issues/247
    assert Detector("Tout philosophe a deux philosophies : la sienne et celle de Spinoza.").language.code == "FR"


if __name__ == "__main__":
    test_Detector()
