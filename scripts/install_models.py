#!/usr/bin/env python
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import argparse

from libretranslate.init import check_and_install_models

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--load_only_lang_codes", type=str, default="")
    parser.add_argument("--update", action='store_true')
    args = parser.parse_args()
    lang_codes = args.load_only_lang_codes.split(",")
    if len(lang_codes) == 0 or lang_codes[0] == '':
        lang_codes = None
    if args.update:
        check_and_install_models(update=True, load_only_lang_codes=lang_codes)
    else:
        check_and_install_models(force=True, load_only_lang_codes=lang_codes)
