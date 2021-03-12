import os
from appdirs import user_data_dir

# override polyglot path
import polyglot
polyglot.polyglot_path = os.path.join(user_data_dir(appname="LibreTranslate", appauthor="uav4geo"), "polyglot_data")


from .main import main
from .manage import manage
