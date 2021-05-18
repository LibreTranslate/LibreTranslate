import string

from argostranslate import translate
from polyglot.detect.base import Detector, UnknownLanguage
from polyglot.transliteration.base import Transliterator

languages = translate.load_installed_languages()


__lang_codes = [l.code for l in languages]


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
            candidates.extend(Detector(t).languages)
        except UnknownLanguage:
            pass

    # total read bytes of the provided text
    read_bytes_total = sum(c.read_bytes for c in candidates)

    # only use candidates that are supported by argostranslate
    candidate_langs = list(
        filter(lambda l: l.read_bytes != 0 and l.code in __lang_codes, candidates)
    )

    # this happens if no language could be detected
    if not candidate_langs:
        # use language "en" by default but with zero confidence
        return [{"confidence": 0.0, "language": "en"}]

    # for multiple occurrences of the same language (can happen on batch detection)
    # calculate the average confidence for each language
    if is_batch:
        temp_average_list = []
        for lang_code in __lang_codes:
            # get all candidates for a specific language
            lc = list(filter(lambda l: l.code == lang_code, candidate_langs))
            if len(lc) > 1:
                # if more than one is present, calculate the average confidence
                lang = lc[0]
                lang.confidence = sum(l.confidence for l in lc) / len(lc)
                lang.read_bytes = sum(l.read_bytes for l in lc)
                temp_average_list.append(lang)
            elif lc:
                # otherwise just add it to the temporary list
                temp_average_list.append(lc[0])

        if temp_average_list:
            # replace the list
            candidate_langs = temp_average_list

    # sort the candidates descending based on the detected confidence
    candidate_langs.sort(
        key=lambda l: (l.confidence * l.read_bytes) / read_bytes_total, reverse=True
    )

    return [{"confidence": l.confidence, "language": l.code} for l in candidate_langs]


def __transliterate_line(transliterator, line_text):
    new_text = []

    # transliteration is done word by word
    for orig_word in line_text.split(" "):
        # remove any punctuation on the right side
        r_word = orig_word.rstrip(string.punctuation)
        r_diff = set(char for char in orig_word) - set(char for char in r_word)
        # and on the left side
        l_word = orig_word.lstrip(string.punctuation)
        l_diff = set(char for char in orig_word) - set(char for char in l_word)

        # the actual transliteration of the word
        t_word = transliterator.transliterate(orig_word.strip(string.punctuation))

        # if transliteration fails, default back to the original word
        if not t_word:
            t_word = orig_word
        else:
            # add back any stripped punctuation
            if r_diff:
                t_word = t_word + "".join(r_diff)
            if l_diff:
                t_word = "".join(l_diff) + t_word

        new_text.append(t_word)

    # rebuild the text
    return " ".join(new_text)


def transliterate(text, target_lang="en"):
    # initialize the transliterator from polyglot
    transliterator = Transliterator(target_lang=target_lang)

    # check for multiline string
    if "\n" in text:
        lines = []
        # process each line separate
        for line in text.split("\n"):
            lines.append(__transliterate_line(transliterator, line))

        # rejoin multiline string
        return "\n".join(lines)
    else:
        return __transliterate_line(transliterator, text)
