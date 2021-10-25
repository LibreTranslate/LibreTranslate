FROM python:3.8

ARG with_models=false
ARG with_expose=true
ARG with_entrypoint=true

WORKDIR /app

RUN pip install --upgrade pip

COPY . .

# check for offline build
RUN if [ "$with_models" = "true" ]; then  \
        # install only the dependencies first
        pip install -e .;  \
        # initialize the language models
        ./install_models.py;  \
    fi

# Install package from source code
RUN pip install .

RUN if [ "$with_expose" = "true" ]; then  \
        EXPOSE 5000;  \
    fi

RUN if [ "$with_entrypoint" = "true" ]; then  \
        ENTRYPOINT [ "libretranslate", "--host", "0.0.0.0" ];  \
    fi
