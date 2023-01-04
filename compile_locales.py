#!/usr/bin/env python
import sys
import os
from babel.messages.frontend import main as pybabel

if __name__ == "__main__":
    locales_dir = os.path.join("libretranslate", "locales")
    if not os.path.isdir(locales_dir):
        os.makedirs(locales_dir)

    print("Compiling locales")
    sys.argv = ["", "compile", "-d", locales_dir]
    pybabel()



