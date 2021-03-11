from argostranslate import translate
from polyglot.detect.base import Detector


languages = translate.load_installed_languages()


__lang_codes = [l.code for l in languages]


def detect_languages(text):
    f = Detector(text).languages

    # get the candidates
    candidate_langs = list(filter(lambda l: l.read_bytes != 0 and l.code in __lang_codes, f))

    # this happens if no language can be detected
    if not candidate_langs:
        # use language "en" by default but with zero confidence
        return [
                    {
                        'confidence': 0.0,
                        'language': "en"
                    }
                ]

    # sort the candidates descending based on the detected confidence
    candidate_langs.sort(key=lambda l: l.confidence, reverse=True)

    return [
                {
                    'confidence': l.confidence,
                    'language': l.code
                }
                for l in candidate_langs
            ]
