#!/usr/bin/env python
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from babel.messages.frontend import main as pybabel

if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == 'mdtable':
        from libretranslate.locales import get_available_locales
        locales = get_available_locales(only_reviewed=False, sort_by_name=True)
        print("Language | Reviewed | Weblate Link")
        print("-------- | -------- | ------------")

        for l in locales:
            link = "https://hosted.weblate.org/translate/libretranslate/app/%s/" % l['code']
            if l['code'] == 'en':
                link = "https://hosted.weblate.org/projects/libretranslate/app/"
            print("{} | {} | {}".format(l['name'], ':heavy_check_mark:' if l['reviewed'] else '', "[Edit](%s)" % link))
    else:
        locales_dir = os.path.join("libretranslate", "locales")
        if not os.path.isdir(locales_dir):
            os.makedirs(locales_dir)

        print("Compiling locales")
        sys.argv = ["", "compile", "-f", "-d", locales_dir]
        pybabel()



