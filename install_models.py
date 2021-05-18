#!/usr/bin/env python

from app.init import check_and_install_models, check_and_install_transliteration

if __name__ == "__main__":
    check_and_install_models(force=True)
    check_and_install_transliteration(force=True)
