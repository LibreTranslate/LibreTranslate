import os
from functools import cache
from flask_babel import gettext as _
from markupsafe import escape, Markup

@cache
def get_available_locales():
    locales_dir = os.path.join(os.path.dirname(__file__), 'locales')
    dirs = [os.path.join(locales_dir, d) for d in os.listdir(locales_dir)]

    return ['en'] + [os.path.basename(d) for d in dirs if os.path.isdir(os.path.join(d, 'LC_MESSAGES'))]

# Javascript code should use _e instead of _
def gettext_escaped(text, **variables):
    return _(text, **variables).replace("'", "\\'")

# HTML should be escaped using _h instead of _
def gettext_html(text, **variables):
    # Translate text without args
    s = str(escape(_(text)))

    v = {}
    if variables:
        for k in variables:
            if hasattr(variables[k], 'unescape'):
                v[k] = variables[k].unescape()
            else:
                v[k] = Markup(variables[k])

    # Variables are assumed to be already escaped and thus safe
    return Markup(s if not v else s % v)