# Contribuyendo

Si desea modificar el código, puede compilar desde el código fuente y ejecutar la API.

## Dependencias de compilación

* cmake

### Debian / Ubuntu

```sh
sudo apt-get install cmake
```

### Fedora / RHEL

```sh
sudo dnf install cmake
```

## Primeros pasos

Instale [`hatch`](https://hatch.pypa.io) para administrar las dependencias del proyecto y ejecutar scripts de desarrollo:

```bash
pipx install hatch
```

Clonar el repositorio:

```bash
git clone https://github.com/LibreTranslate/LibreTranslate.git
cd LibreTranslate
```

Hatch instalará automáticamente las dependencias necesarias en un entorno virtual y habilitará [`pre-commit`](https://pre-commit.com/), que se ejecutará antes de cada confirmación para ejecutar el formateo. Si es necesario, puedes ignorar las comprobaciones de `pre-commit` al confirmar: `git commit --no-verify -m "Fix"`

Ejecutar en desarrollo:

```bash
hatch run dev --debug
```

Luego, abre un navegador web en <http://localhost:5000>

También puedes iniciar una nueva shell en un entorno virtual con libretranslate instalado:

```bash
hatch shell
libretranslate [args]
# O
python main.py [args]
```

> Puedes usar `pip install -e ".[test]"` directamente si no quieres usar Hatch.

## Ejecutar las pruebas

Ejecutar el conjunto de pruebas y las comprobaciones de linting:

```bash
hatch run test
```

Para mostrar todos los `print()` durante la depuración:

```bash
hatch run test -s
```

También puedes ejecutar las pruebas en varias versiones de Python:

```bash
hatch run all:test
```

Puedes limpiar el entorno virtual con:

```bash
hatch env prune
```

## Ejecutar con Docker

Linux/MacOS: `./run.sh [args]`
Windows: `run.bat [args]`

Luego, abre un navegador web en <http://localhost:5000>

## Construir con Docker

```bash
docker build -f docker/Dockerfile [--build-arg with_models=true] -t libretranslate .
```

Si quieres ejecutar la imagen de Docker en un entorno completamente sin conexión, debes agregar el parámetro `--build-arg with_models=true`. Los modelos de lenguaje se descargan durante el proceso de construcción de la imagen. De lo contrario, estos modelos se descargan durante la primera ejecución de la imagen/contenedor.

Ejecute la imagen compilada:

```bash
docker run -it -p 5000:5000 libretranslate [args]
```

O compila y ejecuta con Docker Compose:

```bash
docker compose up -d --build
```

> Puedes modificar el archivo [`docker-compose.yml`](https://github.com/LibreTranslate/LibreTranslate/blob/main/docker-compose.yml) para adaptarlo a tus necesidades de implementación o usar un archivo `docker-compose.prod.yml` adicional para la configuración de tu implementación.
>
> Los modelos se almacenan dentro del contenedor en `/home/libretranslate/.local/share` y `/home/libretranslate/.local/cache`. Puedes usar volúmenes si no quieres volver a descargar los modelos cuando se destruya el contenedor. Para actualizar los modelos, usa el argumento `--update-models`.

## Preguntas frecuentes

### Entorno administrado externamente

Algunos usuarios pueden encontrar el siguiente error al instalar paquetes:

```
error: externally-managed-environment

× Este entorno está administrado externamente
╰─> Para instalar paquetes de Python en todo el sistema, pruebe apt install python3-xyz, donde xyz es el paquete que intenta instalar.

    …
```

Esto ocurre cuando su sistema operativo depende de Python y lo administra para su funcionalidad principal. En este caso, debe instalar y configurar venv (entornos virtuales) para administrar las dependencias del proyecto.

Esto evita que los paquetes pip se instalen en todo el sistema. De esta manera, se evita el riesgo de que los paquetes pip entren en conflicto entre varios proyectos o el sistema operativo.

Referencias:
* [Documentación de venv sobre Python](https://docs.python.org/library/venv.html)

## Otros idiomas

- [English (CONTRIBUTING)](/CONTRIBUTING.md)