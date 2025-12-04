#!/usr/bin/env python
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from libretranslate.main import get_args, get_parser

parser = get_parser()
args = get_args()
for arg in dir(args):
    if not arg.startswith('_'):
        value = getattr(args, arg)
        def_value = parser.get_default(arg)
        if not callable(value) and (value != def_value or arg == 'port' or arg == 'threads'):
            if isinstance(value, str):
                value = value.replace('"', '')
            elif isinstance(value, list):
                value = ",".join(value)
            print(f"export LT_{arg.upper()}={value}")
