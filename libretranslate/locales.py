import os
from functools import cache

@cache
def get_available_locales():
    locales_dir = os.path.join(os.path.dirname(__file__), 'locales')
    dirs = [os.path.join(locales_dir, d) for d in os.listdir(locales_dir)]

    return ['en'] + [os.path.basename(d) for d in dirs if os.path.isdir(os.path.join(d, 'LC_MESSAGES'))]