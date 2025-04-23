FROM python:3.11.11-slim-bullseye AS builder

WORKDIR /app

ARG DEBIAN_FRONTEND=noninteractive
RUN <<EOF
  apt-get update -qq
  apt-get -qqq install --no-install-recommends -y pkg-config gcc g++
  apt-get upgrade --assume-yes
  apt-get clean
  rm -rf /var/lib/apt

  python -mvenv venv
  ./venv/bin/pip install --no-cache-dir --upgrade pip
EOF

COPY . .

# Install package from source code, compile translations
RUN <<EOF
  ./venv/bin/pip install Babel==2.12.1
  ./venv/bin/python scripts/compile_locales.py
  ./venv/bin/pip install torch==2.2.0 --extra-index-url https://download.pytorch.org/whl/cpu
  ./venv/bin/pip install "numpy<2"
  ./venv/bin/pip install .
  ./venv/bin/pip cache purge
EOF

FROM python:3.11.11-slim-bullseye

ARG with_models=false
ARG models=""

ARG api_key=""

RUN <<EOF
  addgroup --system --gid 1032 libretranslate
  adduser --system --uid 1032 libretranslate
  mkdir -p /home/libretranslate/.local
  chown -R libretranslate:libretranslate /home/libretranslate/.local
EOF

USER libretranslate

COPY --from=builder --chown=1032:1032 /app /app
WORKDIR /app

COPY --from=builder --chown=1032:1032 /app/venv/bin/ltmanage /usr/bin/

RUN <<EOF
  if [ "$with_models" = "true" ]; then
    # initialize the language models
    if [ ! -z "$models" ]; then
      ./venv/bin/python scripts/install_models.py --load_only_lang_codes "$models"
    else
      ./venv/bin/python scripts/install_models.py
    fi
  fi
EOF

RUN <<EOF
  if [ ! -z "$api_key" ]; then
    # initialize the API key database
    ./venv/bin/python - <<'EOPython'
from libretranslate.api_keys import Database
from libretranslate.default_values import DEFAULT_ARGUMENTS as DEFARGS
Database(DEFARGS['API_KEYS_DB_PATH'])
EOPython

    # initialize one API key
    ltmanage keys add 120 --key "$api_key"
  fi
EOF

EXPOSE 22
EXPOSE 5000

ENTRYPOINT [ "./venv/bin/libretranslate", "--host", "*" ]
