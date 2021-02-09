import os
from pathlib import Path
from argostranslate import settings, package, translate
import os, glob, shutil, zipfile

def boot():
	check_and_install_models()

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

        print("Loaded support for %s languages (%s models total)!" % (len(translate.load_installed_languages()), len(available_packages)))
	