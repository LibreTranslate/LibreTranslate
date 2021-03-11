import os
from pathlib import Path
from argostranslate import settings, package, translate
import os, glob, shutil, zipfile
from app.language import languages
import polyglot

def boot():
    check_and_install_models()
    check_and_install_transliteration()

def check_and_install_models(force=False):
    if len(package.get_installed_packages()) < 2 or force:
        # Update package definitions from remote
        print("Updating language models")
        package.update_package_index()

        # Load available packages from local package index
        available_packages = package.load_available_packages()
        print("Found %s models" % len(available_packages))

        # Download and install all available packages
        for available_package in available_packages:
            print("Downloading %s (%s) ..." % (available_package, available_package.package_version))
            download_path = available_package.download()
            package.install_from_path(download_path)

        # reload installed languages
        global languages
        languages = translate.load_installed_languages()
        print("Loaded support for %s languages (%s models total)!" % (len(translate.load_installed_languages()), len(available_packages)))


def check_and_install_transliteration(force=False):
    # 'en' is not a supported transliteration language
    transliteration_languages = [l.code for l in languages if l.code != "en"]

    # check installed
    install_needed = []
    if not force:
        t_packages_path = Path(polyglot.polyglot_path) / "transliteration2"
        for lang in transliteration_languages:
            if not (t_packages_path / lang / f"transliteration.{lang}.tar.bz2").exists():
                install_needed.append(lang)
    else:
        install_needed = transliteration_languages

    # install the needed transliteration packages
    if install_needed:
        print(f"Installing transliteration models for the following languages: {', '.join(install_needed)}")

        from polyglot.downloader import Downloader
        downloader = Downloader()

        for lang in install_needed:
            downloader.download(f"transliteration2.{lang}")
