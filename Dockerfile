FROM python:3.8

ARG with_models=false

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

EXPOSE 5000
ENTRYPOINT [ "libretranslate", "--host", "0.0.0.0" ]
