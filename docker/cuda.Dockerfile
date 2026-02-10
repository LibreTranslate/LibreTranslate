FROM nvidia/cuda:12.4.1-runtime-ubuntu22.04 AS builder

WORKDIR /app

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update -qq \
  && apt-get -qqq install --no-install-recommends -y pkg-config gcc g++ python3-dev python3-pip python3-venv git \
  && apt-get upgrade --assume-yes \
  && apt-get clean \
  && rm -rf /var/lib/apt

RUN python3 -m venv venv && ./venv/bin/pip install --no-cache-dir --upgrade pip

COPY . .

# Install package from source code, compile translations
RUN ./venv/bin/pip install Babel==2.12.1 && ./venv/bin/python scripts/compile_locales.py \
  && ./venv/bin/pip install "numpy<2" \
  && ./venv/bin/pip install . \
  && ./venv/bin/pip uninstall -y onnxruntime && ./venv/bin/pip install --no-cache-dir onnxruntime-gpu>=1.10.0 \
  && ./venv/bin/pip cache purge

FROM nvidia/cuda:12.4.1-runtime-ubuntu22.04

ENV ARGOS_DEVICE_TYPE auto
ARG with_models=false
ARG models=""

WORKDIR /app

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update -qq \
  && apt-get -qqq install --no-install-recommends -y python3 python3-pip \
  && apt-get clean \
  && rm -rf /var/lib/apt

RUN ln -s /usr/bin/python3 /usr/bin/python

COPY --from=builder /app /app
ENV PATH="/app/venv/bin:$PATH"

COPY --from=builder /app/venv/bin/ltmanage /usr/bin/

RUN if [ "$with_models" = "true" ]; then  \
  # initialize the language models
  if [ ! -z "$models" ]; then \
  python scripts/install_models.py --load_only_lang_codes "$models";   \
  else \
  python scripts/install_models.py;  \
  fi \
  fi

# Depending on your cuda install you may need to uncomment this line to allow the container to access the cuda libraries
# See: https://docs.nvidia.com/cuda/cuda-installation-guide-linux/index.html#post-installation-actions
# ENV LD_LIBRARY_PATH=/usr/local/cuda/lib:/usr/local/cuda/lib64

EXPOSE 5000
ENTRYPOINT [ "libretranslate", "--host", "*" ]
