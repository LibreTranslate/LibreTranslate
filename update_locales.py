#!/usr/bin/env python
import sys
import os
import re
import polib
from babel.messages.frontend import main as pybabel
from libretranslate.language import load_languages, improve_translation_formatting
from libretranslate.locales import get_available_locales
from translatehtml import translate_html
from libretranslate.app import get_version

# Update strings
if __name__ == "__main__":
    locales_dir = os.path.join("libretranslate", "locales")
    if not os.path.isdir(locales_dir):
        os.makedirs(locales_dir)

    messagespot = os.path.join(locales_dir, "messages.pot")
    print("Updating %s" % messagespot)
    sys.argv = ["", "extract", "-F", "babel.cfg", "-k", "_e _h", 
                "--copyright-holder", "LibreTranslate Authors",
                "--project", "LibreTranslate",
                "--version", get_version(),
                "-o", messagespot, "libretranslate"]
    pybabel()

    # Load list of languages
    print("Loading languages")
    languages = load_languages()
    en_lang = next((l for l in languages if l.code == 'en'), None)
    if en_lang is None:
        print("Error: English model not found. You need it to run this script.")
        exit(1)
    
    lang_codes = [l.code for l in languages if l != "en"]
    lang_codes = ["it"] # TODO REMOVE

    # Init/update
    for l in lang_codes:
        cmd = "init"
        if os.path.isdir(os.path.join(locales_dir, l)):
            cmd = "update"

        sys.argv = ["", cmd, "-i", messagespot, "-d", locales_dir, "-l", l]
        pybabel()
    
    # Automatically translate strings with libretranslate
    # when a language model is available and a string is empty

    locales = get_available_locales()
    for locale in locales:
        if locale == 'en':
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
                placeholders = re.findall(r'%\(?.*?\)?s', text)

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



