import os
import json
from functools import cache
from flask_babel import gettext as _
from flask_babel import lazy_gettext as _lazy

from markupsafe import escape, Markup

@cache
def get_available_locales():
    locales_dir = os.path.join(os.path.dirname(__file__), 'locales')
    dirs = [os.path.join(locales_dir, d) for d in os.listdir(locales_dir)]

    return ['en'] + [os.path.basename(d) for d in dirs if os.path.isdir(os.path.join(d, 'LC_MESSAGES'))]

@cache
def get_alternate_locale_links():
    tmpl = os.environ.get("LT_LOCALE_LINK_TEMPLATE")
    if tmpl is None:
        return []
    
    locales = get_available_locales()
    result = []
    for l in locales:
        link = tmpl.replace("{LANG}", l)
        if l == 'en':
            link = link.replace("en.", "")
        result.append({ 'link': link,'lang': l })
    return result

# Javascript code should use _e instead of _
def gettext_escaped(text, **variables):
    return json.dumps(_(text, **variables))

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

def swag_eval(swag, func):
    # Traverse the swag spec structure
    # and call func on summary and description keys
    for k in swag:
        if k in ['summary', 'description'] and isinstance(swag[k], str) and swag[k] != "":
            swag[k] = func(swag[k])
        elif k == 'tags' and isinstance(swag[k], list):
            swag[k] = [func(v) for v in swag[k]]
        elif isinstance(swag[k], dict):
            swag_eval(swag[k], func)

    return swag

def lazy_swag(swag):
    return swag_eval(swag, _lazy)