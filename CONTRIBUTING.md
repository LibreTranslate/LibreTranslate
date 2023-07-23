# Contributing

If you want to make changes to the code, you can build from source, and run the API.

## Build Dependencies

* cmake

### Debian / Ubuntu

```sh
sudo apt-get install cmake
```

### Fedora / RHEL

```sh
sudo dnf install cmake
```

## Getting Started

Install [`hatch`](https://hatch.pypa.io) to manage the projects dependencies and run dev scripts:

```bash
pipx install hatch
```

Clone the repository:

```bash
git clone https://github.com/LibreTranslate/LibreTranslate.git
cd LibreTranslate
```

Hatch will automatically install the required dependencies in a virtual environment, and enable [`pre-commit`](https://pre-commit.com/), which will run before each commit to run formatting. You can ignore `pre-commit` checks when committing if necessary: `git commit --no-verify -m "Fix"`

Run in development:

```bash
hatch run dev --debug
```

Then open a web browser to <http://localhost:5000>

You can also start a new shell in a virtual environment with libretranslate installed:

```bash
hatch shell
libretranslate [args]
# Or
python main.py [args]
```

> You can still use `pip install -e ".[test]"` directly if you don't want to use hatch.

## Run the tests

Run the test suite and linting checks:

```bash
hatch run test
```

To display all `print()` when debugging:

```bash
hatch run test -s
```

You can also run the tests on multiple python versions:

```bash
hatch run all:test
```

You can clean the virtual environment with:

```bash
hatch env prune
```

## Run with Docker

Linux/macOS: `./run.sh [args]`
Windows: `run.bat [args]`

Then open a web browser to <http://localhost:5000>

## Build with Docker

```bash
docker build -f docker/Dockerfile [--build-arg with_models=true] -t libretranslate .
```

If you want to run the Docker image in a complete offline environment, you need to add the `--build-arg with_models=true` parameter. Then the language models are downloaded during the build process of the image. Otherwise, these models get downloaded on the first run of the image/container.

Run the built image:

```bash
docker run -it -p 5000:5000 libretranslate [args]
```

Or build and run using Docker Compose:

```bash
docker compose up -d --build
```

> Feel free to change the [`docker-compose.yml`](https://github.com/LibreTranslate/LibreTranslate/blob/main/docker-compose.yml) file to adapt it to your deployment needs, or use an extra `docker-compose.prod.yml` file for your deployment configuration.
>
> The models are stored inside the container under `/home/libretranslate/.local/share` and `/home/libretranslate/.local/cache`. Feel free to use volumes if you do not want to redownload the models when the container is destroyed. To update the models, use the `--update-models` argument.

## FAQ

### Externally Managed Environment

Some users may encounter the following error while installing packages:

```
error: externally-managed-environment

× This environment is externally managed
╰─> To install Python packages system-wide, try apt install
    python3-xyz, where xyz is the package you are trying to
    install.

    …
```

This occurs when your operating system depends on and manages Python for core functionality. In this case, you should install and setup venv (virtual environments) to manage project dependencies.

This prevents pip packages from being installed system-wide. This way, there are no risks of pip packages conflicting between multiple projects or the operating system.

References:
* [Python venv documentation](https://docs.python.org/library/venv.html)
