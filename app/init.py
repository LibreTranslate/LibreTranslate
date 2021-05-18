from pathlib import Path

import polyglot
from argostranslate import package, translate

import app.language


def boot(load_only=None):
    try:
        check_and_install_models(load_only_lang_codes=load_only)
        check_and_install_transliteration()
    except Exception as e:
        print("Cannot update models (normal if you're offline): %s" % str(e))


def check_and_install_models(force=False, load_only_lang_codes=None):
    if len(package.get_installed_packages()) < 2 or force:
        # Update package definitions from remote
        print("Updating language models")
        package.update_package_index()

        # Load available packages from local package index
        available_packages = package.load_available_packages()
        print("Found %s models" % len(available_packages))

        if load_only_lang_codes is not None:
            # load_only_lang_codes: List[str] (codes)
            # Ensure the user does not use any unavailable language code.
            unavailable_lang_codes = set(load_only_lang_codes)
            for pack in available_packages:
                unavailable_lang_codes -= {pack.from_code, pack.to_code}
            if unavailable_lang_codes:
                raise ValueError(
                    "Unavailable language codes: %s."
                    % ",".join(sorted(unavailable_lang_codes))
                )
            # Keep only the packages that have both from_code and to_code in our list.
            available_packages = [
                pack
                for pack in available_packages
                if pack.from_code in load_only_lang_codes and pack.to_code in load_only_lang_codes
            ]
            if not available_packages:
                raise ValueError("no available package")
            print("Keep %s models" % len(available_packages))

        # Download and install all available packages
        for available_package in available_packages:
            print(
                "Downloading %s (%s) ..."
                % (available_package, available_package.package_version)
            )
            download_path = available_package.download()
            package.install_from_path(download_path)

        # reload installed languages
        app.language.languages = translate.load_installed_languages()
        print(
            "Loaded support for %s languages (%s models total)!"
            % (len(translate.load_installed_languages()), len(available_packages))
        )


def check_and_install_transliteration(force=False):
    # 'en' is not a supported transliteration language
    transliteration_languages = [
        l.code for l in app.language.languages if l.code != "en"
    ]

    # check installed
    install_needed = []
    if not force:
        t_packages_path = Path(polyglot.polyglot_path) / "transliteration2"
        for lang in transliteration_languages:
            if not (
                t_packages_path / lang / f"transliteration.{lang}.tar.bz2"
            ).exists():
                install_needed.append(lang)
    else:
        install_needed = transliteration_languages

    # install the needed transliteration packages
    if install_needed:
        print(
            f"Installing transliteration models for the following languages: {', '.join(install_needed)}"
        )

        from polyglot.downloader import Downloader

        downloader = Downloader()

        for lang in install_needed:
            downloader.download(f"transliteration2.{lang}")
