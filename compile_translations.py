#!/usr/bin/env python
import sys
import os
from babel.messages.frontend import main as pybabel

if __name__ == "__main__":
    translations_dir = os.path.join("libretranslate", "translations")
    if not os.path.isdir(translations_dir):
        os.makedirs(translations_dir)

    print("Compiling translations")
    sys.argv = ["", "compile", "-d", translations_dir]
    pybabel()



