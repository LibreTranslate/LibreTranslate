#!/usr/bin/env python
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import json
import re

import polib
from babel.messages.frontend import main as pybabel
from flask_swagger import swagger
from translatehtml import translate_html

from libretranslate.app import create_app, get_version
from libretranslate.language import improve_translation_formatting, load_languages
from libretranslate.locales import get_available_locale_codes, swag_eval
from libretranslate.main import get_args

# Update strings
if __name__ == "__main__":
    print("Loading languages")
    languages = load_languages()
    en_lang = next((l for l in languages if l.code == 'en'), None)
    if en_lang is None:
        print("Error: English model not found. You need it to run this script.")
        exit(1)

    locales_dir = os.path.join("libretranslate", "locales")
    if not os.path.isdir(locales_dir):
        os.makedirs(locales_dir)

    # Dump language list so it gets picked up by pybabel
    langs_file = os.path.join(locales_dir, ".langs.py")
    lang_names = {}
    with open(langs_file, 'w') as f:
        for l in languages:
            f.write("_(%s)\n" % json.dumps(l.name))
            lang_names[l.name] = True

        # Additional names that might be missing
        for l in ["Serbian", "Ukrainian", "Vietnamese"]:
            if not l in lang_names:
                f.write("_(%s)\n" % json.dumps(l))
                lang_names[l] = True
    print("Wrote %s" % langs_file)

    # Dump swagger strings
    args = get_args()
    app = create_app(args)
    swag = swagger(app)

    swag_strings = []
    def add_swag_string(s):
        if not s in swag_strings:
            swag_strings.append(s)
    swag_eval(swag, add_swag_string)

    swag_file = os.path.join(locales_dir, ".swag.py")
    with open(swag_file, 'w') as f:
        for ss in swag_strings:
            f.write("_(%s)\n" % json.dumps(ss))
    print("Wrote %s" % swag_file)

    messagespot = os.path.join(locales_dir, "messages.pot")
    print("Updating %s" % messagespot)
    sys.argv = ["", "extract", "-F", "babel.cfg", "-k", "_e _h",
                "--copyright-holder", "LibreTranslate Authors",
                "--project", "LibreTranslate",
                "--version", get_version(),
                "-o", messagespot, "libretranslate"]
    pybabel()

    lang_map = {
        'zt': 'zh_Hant'
    }
    lang_codes = [lang_map.get(l.code, l.code) for l in languages if l.code != "en"]
    all_folders = [d for d in os.listdir(locales_dir) if os.path.isdir(os.path.join(locales_dir, d))]
    review_map = {}

    # Init/update
    for l in all_folders:
        cmd = "init"
        if os.path.isdir(os.path.join(locales_dir, l, "LC_MESSAGES")):
            cmd = "update"

        sys.argv = ["", cmd, "-i", messagespot, "-d", locales_dir, "-l", l] + (["--no-fuzzy-matching"] if cmd == "update" else [])
        pybabel()

        meta_file = os.path.join(locales_dir, l, "meta.json")
        reviewed = False
        if not os.path.isfile(meta_file):
            with open(meta_file, 'w') as f:
                f.write(json.dumps({
                    'name': l if l not in lang_codes else next(lang.name for lang in languages if lang_map.get(lang.code, lang.code) == l),
                    'reviewed': False
                }, indent=4))
                print("Wrote %s" % meta_file)
        else:
            with open(meta_file) as f:
                reviewed = json.loads(f.read()).get('reviewed', False)

        review_map[l] = reviewed

    # Automatically translate strings with libretranslate
    # when a language model is available and a string is empty

    locales = get_available_locale_codes(only_reviewed=False)
    for locale in locales:
        if locale == 'en':
            continue
        if review_map.get(locale):
            # Don't automatically translate reviewed languages
            continue

        tgt_lang = next((l for l in languages if l.code == locale), None)

        if tgt_lang is None:
            # We cannot translate
            continue

        translator = en_lang.get_translation(tgt_lang)

        messages_file = os.path.join(locales_dir, locale, "LC_MESSAGES", 'messages.po')
        if os.path.isfile(messages_file):
            print("Translating '%s'" % locale)
            pofile = polib.pofile(messages_file)
            c = 0

            for entry in pofile.untranslated_entries():
                text = entry.msgid

                # Extract placeholders
                placeholders = re.findall(r'%\(?[^\)]*\)?s', text)

                for p in range(0, len(placeholders)):
                    text = text.replace(placeholders[p], "<x>%s</x>" % p)

                if len(placeholders) > 0:
                    translated = str(translate_html(translator, text))
                else:
                    translated = improve_translation_formatting(text, translator.translate(text))

                # Restore placeholders
                for p in range(0, len(placeholders)):
                    tag = "<x>%s</x>" % p
                    if tag in translated:
                        translated = translated.replace(tag, placeholders[p])
                    else:
                        # Meh, append
                        translated += " " + placeholders[p]

                print(entry.msgid, " --> ", translated)
                entry.msgstr = translated
                c += 1

            if c > 0:
                pofile.save(messages_file)
                print("Saved %s" % messages_file)



