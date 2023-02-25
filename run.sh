#!/bin/bash
set -eo pipefail
__dirname=$(cd "$(dirname "$0")"; pwd -P)
cd "${__dirname}"

platform="Linux" # Assumed
uname=$(uname)
case $uname in
    "Darwin")
    platform="MacOS / OSX"
    ;;
    MINGW*)
    platform="Windows"
    ;;
esac

usage(){
  echo "Usage: $0 [--port N]"
  echo
  echo "Run LibreTranslate using docker."
  echo
  exit
}

export LT_PORT=5000

# Parse args for overrides
ARGS=()
while [[ $# -gt 0 ]]
do
key="$1"
case $key in
    --port)
    export LT_PORT="$2"
    ARGS+=("$1")
    ARGS+=("$2") # save it in an array for later
    shift # past argument
    shift # past value
    ;;
    --debug)
    export LT_DEBUG=YES
    ARGS+=("$1")
    shift # past argument
    ;;
    --api-keys)
    export DB_VOLUME="-v lt-db:/app/db"
    ARGS+=("$1")
    shift # past argument
    ;;
    --help)
    usage
    ;;
    *)    # unknown option
    ARGS+=("$1")
    shift # past argument
    ;;
esac
done

# $1 = command | $2 = help_text | $3 = install_command (optional)
check_command(){
    hash "$1" 2>/dev/null || not_found=true
    if [[ $not_found ]]; then
        check_msg_prefix="Checking for $1... "

        # Can we attempt to install it?
        if [[ -n "$3" ]]; then
            echo -e "$check_msg_prefix \033[93mnot found, we'll attempt to install\033[39m"
            $3 || sudo $3

            # Recurse, but don't pass the install command
            check_command "$1" "$2"
        else
            check_msg_result="\033[91m can't find $1! Check that the program is installed and that you have added the proper path to the program to your PATH environment variable before launching the program. If you change your PATH environment variable, remember to close and reopen your terminal. $2\033[39m"
        fi
    else
        check_msg_prefix="Checking for $1... "
        check_msg_result="\033[92m found\033[39m"
    fi

    echo -e "$check_msg_prefix $check_msg_result"
    if [[ $not_found ]]; then
        return 1
    fi
}

environment_check(){
    check_command "docker" "https://www.docker.com/"
}

environment_check
docker run -ti --rm -p $LT_PORT:$LT_PORT $DB_VOLUME -v lt-local:/home/libretranslate/.local libretranslate/libretranslate ${ARGS[@]}
