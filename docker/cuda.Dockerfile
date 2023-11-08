FROM nubitic/l4t-pytorch:r35.1.0-pth1.12-py3

ENV ARGOS_DEVICE_TYPE cuda
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
RUN rm -rf /usr/bin/python
RUN ln -s /usr/bin/python3 /usr/bin/python

RUN git clone --recursive https://github.com/OpenNMT/CTranslate2.git
RUN rm /app/CTranslate2/CMakeLists.txt
COPY CMakeLists-CTranslate2.txt CTranslate2/CMakeLists.txt
RUN mkdir /app/CTranslate2/build
RUN cd /app/CTranslate2/build && cmake -DWITH_CUDA=ON -DWITH_MKL=OFF -DWITH_CUDNN=ON ..
RUN cd /app/CTranslate2/build && make -j4
RUN cd /app/CTranslate2/build && sudo make install
RUN sudo ldconfig
RUN sudo apt-get install python3-dev
RUN cd /app/CTranslate2/python && pip install -r install_requirements.txt
RUN cd /app/CTranslate2/python && python setup.py bdist_wheel
RUN cd /app/CTranslate2/python && pip install dist/*.whl

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
    && pip3 install . \
    && pip3 cache purge

# Depending on your cuda install you may need to uncomment this line to allow the container to access the cuda libraries
# See: https://docs.nvidia.com/cuda/cuda-installation-guide-linux/index.html#post-installation-actions
# ENV LD_LIBRARY_PATH=/usr/local/cuda/lib:/usr/local/cuda/lib64
ENV LT_DEBUG YES
EXPOSE 5000
ENTRYPOINT [ "libretranslate", "--debug", "--host", "0.0.0.0" ]
