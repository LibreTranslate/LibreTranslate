FROM nvidia/cuda:12.4.1-devel-ubuntu20.04

ENV ARGOS_DEVICE_TYPE auto
ARG with_models=false
ARG models=""

WORKDIR /app

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update -qq \
    && apt-get -qqq install --no-install-recommends -y libicu-dev libaspell-dev libcairo2 libcairo2-dev pkg-config gcc g++ python3.8-dev python3-pip libpython3.8-dev\
    && apt-get upgrade --assume-yes \
    && apt-get clean \
    && rm -rf /var/lib/apt

RUN pip3 install --no-cache-dir --upgrade pip && apt-get remove python3-pip --assume-yes

RUN ln -s /usr/bin/python3 /usr/bin/python

RUN pip3 install --no-cache-dir torch==1.12.0+cu116 -f https://download.pytorch.org/whl/torch_stable.html

COPY . .

RUN if [ "$with_models" = "true" ]; then  \
    # install only the dependencies first
    pip3 install --no-cache-dir -e .;  \
    # initialize the language models
    if [ ! -z "$models" ]; then \
    ./scripts/install_models.py --load_only_lang_codes "$models";   \
    else \
    ./scripts/install_models.py;  \
    fi \
    fi

# Install package from source code
RUN pip3 install Babel==2.12.1 && python3 scripts/compile_locales.py \
    && pip3 install "numpy<2" \
    && pip3 install . \
    && pip3 cache purge

# Depending on your cuda install you may need to uncomment this line to allow the container to access the cuda libraries
# See: https://docs.nvidia.com/cuda/cuda-installation-guide-linux/index.html#post-installation-actions
# ENV LD_LIBRARY_PATH=/usr/local/cuda/lib:/usr/local/cuda/lib64

EXPOSE 5000
ENTRYPOINT [ "libretranslate", "--host", "*" ]
