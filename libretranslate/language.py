
from functools import lru_cache

from argostranslate import translate

from libretranslate.detect import Detector

__languages = None

def load_languages():
    global __languages

    if __languages is None or len(__languages) == 0:
        __languages = translate.get_installed_languages()

    return __languages

@lru_cache(maxsize=None)
def load_lang_codes():
    languages = load_languages()
    return tuple(l.code for l in languages)

def detect_languages(text):
    # detect batch processing
    if isinstance(text, list):
        is_batch = True
    else:
        is_batch = False
        text = [text]

    lang_codes = load_lang_codes()

    # get the candidates
    candidates = []
    for t in text:
        try:
            d = Detector(lang_codes).detect(t)
            for i in range(len(d)):
                d[i].text_length = len(t)
            candidates.extend(d)
        except Exception as e:
            print(str(e))

    # total read bytes of the provided text
    text_length_total = sum(c.text_length for c in candidates)

    # this happens if no language could be detected
    if not candidates:
        # use language "en" by default but with zero confidence
        return [{"confidence": 0.0, "language": "en"}]

    # for multiple occurrences of the same language (can happen on batch detection)
    # calculate the average confidence for each language
    if is_batch:
        temp_average_list = []
        for lang_code in lang_codes:
            # get all candidates for a specific language
            lc = list(filter(lambda l: l.code == lang_code, candidates))
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
            candidates = temp_average_list

    # sort the candidates descending based on the detected confidence
    candidates.sort(
        key=lambda l: (l.confidence * l.text_length) / text_length_total, reverse=True
    )

    return [{"confidence": l.confidence, "language": l.code} for l in candidates]


def improve_translation_formatting(source, translation, improve_punctuation=True, remove_single_word_duplicates=True):
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

    # A workaround for certain language models that output
    # the single word repeated ad-infinitum (the "salad" bug)
    # https://github.com/LibreTranslate/LibreTranslate/issues/46
    if remove_single_word_duplicates:
        if len(source) < 20 and source.count(" ") == 0 and translation.count(" ") > 0:
            bow = translation.split()
            count = {}
            for word in bow:
                count[word] = count.get(word, 0) + 1

            for word in count:
                if count[word] / len(count) >= 2:
                    translation = bow[0]
                    break

    if source.islower():
        return translation.lower()

    if source.isupper():
        return translation.upper()

    if len(translation) == 0:
        return source

    if source[0].islower():
        return translation[0].lower() + translation[1:]

    if source[0].isupper():
        return translation[0].upper() + translation[1:]

    return translation

