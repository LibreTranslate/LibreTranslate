
from argostranslate import package, translate
from packaging import version

import libretranslate.language


def boot(load_only=None, update_models=False, install_models=False):
    try:
        if update_models:
            check_and_install_models(load_only_lang_codes=load_only, update=update_models)
        else:
            check_and_install_models(force=install_models, load_only_lang_codes=load_only)
    except Exception as e:
        print("Cannot update models (normal if you're offline): %s" % str(e))


def check_and_install_models(force=False, load_only_lang_codes=None,update=False):
    if len(package.get_installed_packages()) < 2 or force or update:
        # Update package definitions from remote
        print("Updating language models")
        package.update_package_index()

        # Load available packages from local package index
        available_packages = package.get_available_packages()
        installed_packages = package.get_installed_packages()
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
            update = False
            if not force:
                for pack in installed_packages:
                    if (
                            pack.from_code == available_package.from_code
                            and pack.to_code == available_package.to_code
                        ):
                        update = True
                        if version.parse(pack.package_version) < version.parse(available_package.package_version):
                            print(
                                f"Updating {available_package} ({pack.package_version}->{available_package.package_version}) ..."
                            )
                            pack.update()
            if not update:
                print(
                    f"Downloading {available_package} ({available_package.package_version}) ..."
                )
                available_package.install()

        # reload installed languages
        libretranslate.language.languages = translate.get_installed_languages()
        print(
            f"Loaded support for {len(translate.get_installed_languages())} languages ({len(available_packages)} models total)!"
        )
