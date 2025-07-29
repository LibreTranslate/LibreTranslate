# cuda.Dockerfile - Fixed version with proper user permissions
FROM nvidia/cuda:12.4.1-devel-ubuntu20.04 as builder

WORKDIR /app

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update -qq \
  && apt-get -qqq install --no-install-recommends -y pkg-config gcc g++ \
  && apt-get upgrade --assume-yes \
  && apt-get clean \
  && rm -rf /var/lib/apt

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.11 \
    python3.11-distutils \
    python3.11-venv \
    python3-pip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Update pip
RUN python3.11 -m pip install --upgrade pip setuptools wheel

# Create virtual environment
RUN python3.11 -m venv venv

# Copy application code
COPY . .

# Install package from source code, compile translations
RUN ./venv/bin/pip install Babel==2.12.1 && ./venv/bin/python scripts/compile_locales.py \
  && ./venv/bin/pip install torch==2.2.0 --extra-index-url https://download.pytorch.org/whl/cu118 \
  && ./venv/bin/pip install "numpy<2" \
  && ./venv/bin/pip install . \
  && ./venv/bin/pip cache purge

# Final stage
FROM nvidia/cuda:12.4.1-runtime-ubuntu20.04

ARG with_models=false
ARG models=""

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.11 \
    python3.11-distutils \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create the libretranslate user and group
RUN addgroup --system --gid 1032 libretranslate && \
    adduser --system --uid 1032 --gid 1032 libretranslate && \
    mkdir -p /home/libretranslate/.local && \
    chown -R libretranslate:libretranslate /home/libretranslate/.local

# Switch to the libretranslate user
USER libretranslate

# Copy the application with proper ownership
COPY --from=builder --chown=1032:1032 /app /app
WORKDIR /app

# Copy ltmanage binary with proper ownership
COPY --from=builder --chown=1032:1032 /app/venv/bin/ltmanage /usr/bin/

# Install models if requested
RUN if [ "$with_models" = "true" ]; then \
  # initialize the language models
  if [ ! -z "$models" ]; then \
    ./venv/bin/python scripts/install_models.py --load_only_lang_codes "$models"; \
  else \
    ./venv/bin/python scripts/install_models.py; \
  fi \
fi

# Set environment variables for CUDA
ENV NVIDIA_VISIBLE_DEVICES all
ENV NVIDIA_DRIVER_CAPABILITIES compute,utility

EXPOSE 5000
ENTRYPOINT [ "./venv/bin/libretranslate", "--host", "*" ]
