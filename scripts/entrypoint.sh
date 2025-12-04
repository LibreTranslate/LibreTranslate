#!/bin/bash

set -eo pipefail
__dirname=$(cd "$(dirname "$0")"; pwd -P)
cd "${__dirname}/.."

echo ""
echo "░█░░░▀█▀░█▀▄░█▀▄░█▀▀░▀█▀░█▀▄░█▀█░█▀█░█▀▀░█░░░█▀█░▀█▀░█▀▀"
echo "░█░░░░█░░█▀▄░█▀▄░█▀▀░░█░░█▀▄░█▀█░█░█░▀▀█░█░░░█▀█░░█░░█▀▀"
echo "░▀▀▀░▀▀▀░▀▀░░▀░▀░▀▀▀░░▀░░▀░▀░▀░▀░▀░▀░▀▀▀░▀▀▀░▀░▀░░▀░░▀▀▀"

echo "v$(cat VERSION)"
echo ""

echo Booting...

if [ -f ./venv/bin/libretranslate ]; then
    LT_POWERCYCLE=1 ./venv/bin/libretranslate "$@"
else
    echo "WARNING: Cannot powercycle LibreTranslate (if you are in development mode, that's fine..)"
fi

eval $(./venv/bin/python ./scripts/print_args_env.py "$@")
PROMETHEUS_MULTIPROC_DIR="${__dirname}/../db/prometheus" ./venv/bin/gunicorn -c scripts/gunicorn_conf.py --workers $LT_THREADS --max-requests 250 --timeout 2400 --bind [::]:$LT_PORT 'wsgi:app'

