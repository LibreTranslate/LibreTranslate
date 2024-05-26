import sys

from libretranslate import main


def app(*args, **kwargs):
    sys.argv = ['--wsgi']
    for k in kwargs:
        ck = k.replace("_", "-")
        if isinstance(kwargs[k], bool) and kwargs[k]:
            sys.argv.append("--" + ck)
        else:
            sys.argv.append("--" + ck)
            sys.argv.append(kwargs[k])

    instance = main()

    if len(kwargs) == 0:
        return instance
    else:
        return instance(*args, **kwargs)
