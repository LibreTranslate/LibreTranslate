import os
from pathlib import Path
from argostranslate import settings

INSTALLED_MODELS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "installed_models"))
os.environ["ARGOS_TRANSLATE_PACKAGES_DIR"] = INSTALLED_MODELS_DIR
settings.package_dirs = [Path(INSTALLED_MODELS_DIR)]

from argostranslate import translate
import os, glob, shutil, zipfile

def boot():
	check_and_install_models()

def check_and_install_models(force=False):
	if os.path.exists(INSTALLED_MODELS_DIR) and not force:
		return

	if os.path.exists(INSTALLED_MODELS_DIR):
		print("Removing old %s" % INSTALLED_MODELS_DIR)
		shutil.rmtree(INSTALLED_MODELS_DIR)

	print("Creating %s" % INSTALLED_MODELS_DIR)
	os.makedirs(INSTALLED_MODELS_DIR, exist_ok=True)


	for f in glob.glob("models/**.argosmodel"):
		print("Installing %s..." % f)
		with zipfile.ZipFile(f, 'r') as zip:
			zip.extractall(path=INSTALLED_MODELS_DIR)

	print("Installed %s language models!" % (len(translate.load_installed_languages())))
	