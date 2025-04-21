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

ARG root_password=""
ARG api_key=""

ENV ENABLE_SSHD=${root_password:+true}

RUN <<EOF
  if [ "$ENABLE_SSHD" = "true" ]; then
    # sshd
    mkdir /var/run/sshd
    apt-get update -qq
    apt-get -qqq install --no-install-recommends -y openssh-server
    apt-get clean
    rm -rf /var/lib/apt

    # sshd_config
    echo "root:${root_password}" | chpasswd
    sed -i 's/^#?\(PermitRootLogin\) .*$/\1 yes/'        /etc/ssh/sshd_config
    sed -i 's/^#?\(PasswordAuthentication\) .*$/\1 yes/' /etc/ssh/sshd_config
    sed -i 's/^#?\(UsePAM\) .*$/\1 no/'                  /etc/ssh/sshd_config
  fi
EOF

COPY --from=builder --chown=root:root /app /app
WORKDIR /app

COPY --from=builder --chown=root:root /app/venv/bin/ltmanage /usr/bin/

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

# entry point
RUN <<EOF
  cat >'/app/start.sh' <<EOENTRY
#!/bin/sh
set -e

if [ "$ENABLE_SSHD" = "true" ]; then
  service ssh start &
fi

/app/venv/bin/libretranslate --host '*'

exit 0
EOENTRY
  chmod 755 /app/start.sh
EOF
ENTRYPOINT [ "/app/start.sh" ]
