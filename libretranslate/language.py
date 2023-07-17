
from argostranslate import translate

from libretranslate.detect import Detector, UnknownLanguageError

__languages = None

def load_languages():
    global __languages

    if __languages is None or len(__languages) == 0:
        __languages = translate.get_installed_languages()

    return __languages

def detect_languages(text):
    # detect batch processing
    if isinstance(text, list):
        is_batch = True
    else:
        is_batch = False
        text = [text]

    # get the candidates
    candidates = []
    for t in text:
        try:
            d = Detector(t).languages
            for i in range(len(d)):
                d[i].text_length = len(t)
            candidates.extend(d)
        except UnknownLanguageError:
            pass

    # total read bytes of the provided text
    text_length_total = sum(c.text_length for c in candidates)

    # Load language codes
    languages = load_languages()
    lang_codes = [l.code for l in languages]

    # only use candidates that are supported by argostranslate
    candidate_langs = list(
        filter(lambda l: l.text_length != 0 and l.code in lang_codes, candidates)
    )

    # this happens if no language could be detected
    if not candidate_langs:
        # use language "en" by default but with zero confidence
        return [{"confidence": 0.0, "language": "en"}]

    # for multiple occurrences of the same language (can happen on batch detection)
    # calculate the average confidence for each language
    if is_batch:
        temp_average_list = []
        for lang_code in lang_codes:
            # get all candidates for a specific language
            lc = list(filter(lambda l: l.code == lang_code, candidate_langs))
            if len(lc) > 1:
                # if more than one is present, calculate the average confidence
                lang = lc[0]
                lang.confidence = sum(l.confidence for l in lc) / len(lc)
                lang.text_length = sum(l.text_length for l in lc)
                temp_average_list.append(lang)
            elif lc:
                # otherwise just add it to the temporary list
                temp_average_list.append(lc[0])

        if temp_average_list:
            # replace the list
            candidate_langs = temp_average_list

    # sort the candidates descending based on the detected confidence
    candidate_langs.sort(
        key=lambda l: (l.confidence * l.text_length) / text_length_total, reverse=True
    )

    return [{"confidence": l.confidence, "language": l.code} for l in candidate_langs]


def improve_translation_formatting(source, translation, improve_punctuation=True):
    source = source.strip()

    if not len(source):
        return ""

    if not len(translation):
        return source

    if improve_punctuation:
        source_last_char = source[len(source) - 1]
        translation_last_char = translation[len(translation) - 1]

        punctuation_chars = ['!', '?', '.', ',', ';', '。']
        if source_last_char in punctuation_chars:
            if translation_last_char != source_last_char:
                if translation_last_char in punctuation_chars:
                    translation = translation[:-1]

                translation += source_last_char
        elif translation_last_char in punctuation_chars:
            translation = translation[:-1]

    if source.islower():
        return translation.lower()

    if source.isupper():
        return translation.upper()

    if source[0].islower():
        return translation[0].lower() + translation[1:]

    if source[0].isupper():
        return translation[0].upper() + translation[1:]

    return translation

