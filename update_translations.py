#!/usr/bin/env python
import sys
import os
from babel.messages.frontend import main as pybabel
from libretranslate.language import load_languages

# Update strings
if __name__ == "__main__":
    translations_dir = os.path.join("libretranslate", "translations")
    if not os.path.isdir(translations_dir):
        os.makedirs(translations_dir)

    messagespot = os.path.join(translations_dir, "messages.pot")
    print("Updating %s" % messagespot)
    sys.argv = ["", "extract", "-F", "babel.cfg", "-o", messagespot, "libretranslate"]
    pybabel()

    # Load list of languages
    print("Loading languages")
    languages = [l.code for l in load_languages() if l != "en"]
    print(languages)
    languages = ["it"]

    for l in languages:
        cmd = "init"
        if os.path.isdir(os.path.join(translations_dir, l)):
            cmd = "update"

        sys.argv = ["", cmd, "-i", messagespot, "-d", translations_dir, "-l", l]
        pybabel()

