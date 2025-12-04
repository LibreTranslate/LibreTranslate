#!/bin/bash
__dirname=$(cd "$(dirname "$0")"; pwd -P)
cd "${__dirname}/.."

echo ""
echo "░█░░░▀█▀░█▀▄░█▀▄░█▀▀░▀█▀░█▀▄░█▀█░█▀█░█▀▀░█░░░█▀█░▀█▀░█▀▀"
echo "░█░░░░█░░█▀▄░█▀▄░█▀▀░░█░░█▀▄░█▀█░█░█░▀▀█░█░░░█▀█░░█░░█▀▀"
echo "░▀▀▀░▀▀▀░▀▀░░▀░▀░▀▀▀░░▀░░▀░▀░▀░▀░▀░▀░▀▀▀░▀▀▀░▀░▀░░▀░░▀▀▀"

echo "v$(cat VERSION)"
echo ""

echo Booting...
touch /tmp/booting.flag

if [[ -f ./venv/bin/libretranslate ]]; then
    LT_POWERCYCLE=1 ./venv/bin/libretranslate "$@"
else
    echo "WARNING: Cannot powercycle LibreTranslate (if you are in development mode, that's fine..)"
fi

rm -f /tmp/booting.flag

eval $(./venv/bin/python ./scripts/print_args_env.py "$@")

if [[ $LT_HOST == "127.0.0.1" ]]; then
    # Default
    BIND_ADDR="0.0.0.0"
    IPV6_STATUS=$(cat /proc/sys/net/ipv6/conf/all/disable_ipv6)
    if [[ $IPV6_STATUS -eq 0 ]]; then
        BIND_ADDR="[::]"
    fi
else
    BIND_ADDR="$LT_HOST"
fi

PROMETHEUS_MULTIPROC_DIR="${__dirname}/../db/prometheus" ./venv/bin/gunicorn -c scripts/gunicorn_conf.py --workers $LT_THREADS --max-requests 250 --timeout 2400 --bind $BIND_ADDR:$LT_PORT 'wsgi:app'

