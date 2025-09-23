# LibreTranslate

[Pruébalo en línea!](https://libretranslate.com) | [Documentación de la API](https://libretranslate.com/docs) | [Foro de la Comunidad](https://community.libretranslate.com/) | [Bluesky](https://bsky.app/profile/libretranslate.com)

[![Versiones de python](https://img.shields.io/pypi/pyversions/libretranslate)](https://pypi.org/project/libretranslate) [![Ejecutar Pruebas](https://github.com/LibreTranslate/LibreTranslate/workflows/Run%20tests/badge.svg)](https://github.com/LibreTranslate/LibreTranslate/actions?query=workflow%3A%22Run+tests%22) [![Crear y Publicar Imagen de Docker](https://github.com/LibreTranslate/LibreTranslate/actions/workflows/publish-docker.yml/badge.svg)](https://github.com/LibreTranslate/LibreTranslate/actions/workflows/publish-docker.yml) [![Publicar paquete](https://github.com/LibreTranslate/LibreTranslate/actions/workflows/publish-package.yml/badge.svg)](https://github.com/LibreTranslate/LibreTranslate/actions/workflows/publish-package.yml) [![Increible Technologia Humana](https://raw.githubusercontent.com/humanetech-community/awesome-humane-tech/main/humane-tech-badge.svg?sanitize=true)](https://codeberg.org/teaserbot-labs/delightful-humane-design)

API de traducción automática gratuita y de código abierto, completamente alojada en el propio servidor. A diferencia de otras API, no depende de proveedores propietarios como Google o Azure para realizar las traducciones. En su lugar, su motor de traducción se basa en código abierto. [Argos Translate](https://github.com/argosopentech/argos-translate) libreria.

![Traducción](https://github.com/user-attachments/assets/457696b5-dbff-40ab-a18e-7bfb152c5121)

[Pruébalo en línea!](https://libretranslate.com) | [Documentación de la API](https://libretranslate.com/docs)

## Ejemplos de la API

### Básico

Solicitud:

```javascript
const res = await fetch("https://libretranslate.com/translate", {
  method: "POST",
  body: JSON.stringify({
    q: "Hello!",
    source: "en",
    target: "es",
  }),
  headers: { "Content-Type": "application/json" },
});

console.log(await res.json());
```

Respuesta:

```javascript
{
    "translatedText": "¡Hola!"
}
```

Lista de códigos de idiomas: https://libretranslate.com/languages

### Detección automática de idioma

Solicitud:

```javascript
const res = await fetch("https://libretranslate.com/translate", {
  method: "POST",
  body: JSON.stringify({
    q: "Ciao!",
    source: "auto",
    target: "es",
  }),
  headers: { "Content-Type": "application/json" },
});

console.log(await res.json());
```

Respuesta:

```javascript
{
    "detectedLanguage": {
        "confidence": 83,
        "language": "it"
    },
    "translatedText": "Adios!"
}
```

### HTML

Solicitud:

```javascript
const res = await fetch("https://libretranslate.com/translate", {
  method: "POST",
  body: JSON.stringify({
    q: '<p class="green">Hello!</p>',
    source: "en",
    target: "es",
    format: "html",
  }),
  headers: { "Content-Type": "application/json" },
});

console.log(await res.json());
```

Respuesta:

```javascript
{
    "translatedText": "<p class=\"green\">¡Hola!</p>"
}
```

### Traducciones Alternativas

Solicitud:

```javascript
const res = await fetch("https://libretranslate.com/translate", {
  method: "POST",
  body: JSON.stringify({
    q: "Hello",
    source: "en",
    target: "it",
    format: "text",
    alternatives: 3,
  }),
  headers: { "Content-Type": "application/json" },
});

console.log(await res.json());
```

Respuesta:

```javascript
{
    "alternatives": [
        "Salve",
        "Pronto"
    ],
    "translatedText": "Ciao"
}
```

## Instalar y Ejecutar

Puedes ejecutar tu propio servidor API con solo unas pocas líneas de configuración!

Asegúrate de tener instalado Python (se recomienda la versión 3.8 o superior) y, a continuación, simplemente ejecuta:

```bash
pip install libretranslate
libretranslate [args]
```

Luego abra un navegador web para <http://localhost:5000>

De forma predeterminada, LibreTranslate instalará compatibilidad con todos los idiomas disponibles. Para cargar solo ciertos idiomas y reducir el tiempo de inicio, puede usar el argumento **--load-only**:

```bash
libretranslate --load-only en,es,fr
```

Consulte también los demás [arguments](#settings--flags) a continuación.

En Ubuntu 20.04, también puede usar el script de instalación disponible en <https://github.com/argosopentech/LibreTranslate-init> 

## Ejecutar con Docker

También puede ejecutar la aplicación con [docker](https://docker.com):

### Linux/macOS

```bash
./run.sh [args]
```

### Windows

```bash
run.bat [args]
```

## Compilación y ejecución

Consulta [CONTRIBUTING.md](./CONTRIBUTING.md) para obtener información sobre cómo compilar y ejecutar el proyecto tú mismo.

### CUDA

Puedes usar la aceleración por hardware para acelerar las traducciones en un equipo con GPU con CUDA 12.4.1 y [nvidia-docker](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html) instalados.

Ejecuta esta versión con:

```bash
docker compose -f docker-compose.cuda.yml up -d --build
```

## Argumentos

Los argumentos que se pasan al proceso o se configuran mediante variables de entorno se dividen en dos tipos.

- Ajustes o indicadores de tiempo de ejecución que se utilizan para alternar modos de ejecución específicos o deshabilitar partes de la aplicación. Actúan como un interruptor al agregarse o eliminarse.

- Parámetros de configuración para establecer varios límites y configurar la aplicación. Estos requieren que se pase un parámetro para funcionar. Si se eliminan, se utilizan los parámetros predeterminados.

### Configuración / Indicadores


| Argumento                     | Descripción                                                                                                 | Configuración predeterminada                    | Sobre nombre                      |
| ----------------------------- | ----------------------------------------------------------------------------------------------------------- | ---------------------------------- | ------------------------------ |
| --debug                       | Habilitar entorno de depuración                                                                                    | `Desactivado`                         | LT_DEBUG                       |
| --ssl                         | Si habilitar SSL                                                                                       | `Desactivado`                         | LT_SSL                         |
| --api-keys                    | Habilitar la base de datos de claves API para los límites de velocidad por cliente cuando se alcanza --req-limit                             | `No utilice claves API`               | LT_API_KEYS                    |
| --require-api-key-origin      | Requerir el uso de una clave API para el acceso programático a la API, a menos que el origen de la solicitud coincida con este dominio | `Sin restricciones sobre el origen del dominio` | LT_REQUIRE_API_KEY_ORIGIN      |
| --require-api-key-secret      | Requerir el uso de una clave API para el acceso programático a la API, a menos que el cliente también envíe una coincidencia secreta   | `No se requieren secretos`    | LT_REQUIRE_API_KEY_SECRET      |
| --require-api-key-fingerprint | Requerir el uso de una clave API para el acceso programático a la API, a menos que el cliente también coincida con una huella digital  | `No se requieren huellas digitales`       | LT_REQUIRE_API_KEY_FINGERPRINT |
| --under-attack                | Habilitar el modo bajo ataque. Cuando está habilitado, las solicitudes deben realizarse con una clave API.      | `Desactivado`                         | LT_UNDER_ATTACK                |
| --suggestions                 | Permitir sugerencias de usuarios                                                                                    | `Desactivado`                         | LT_SUGGESTIONS                 |
| --disable-files-translation   | Deshabilitar la traducción de archivos                                                                                   | `Se permite la traducción de archivos`         | LT_DISABLE_FILES_TRANSLATION   |
| --disable-web-ui              | Deshabilitar la interfaz web                                                                                              | `Interfaz de usuario web habilitada`                   | LT_DISABLE_WEB_UI              |
| --update-models               | Actualizar los modelos de lenguaje al inicio                                                                           | `Solo se activa si no se encuentran modelos`       | LT_UPDATE_MODELS               |
| --metrics                     | Habilitar el punto final /metrics para exportar [Prometheus](https://prometheus.io/) métricas de uso               | `Desactivado`                         | LT_METRICS                     |

### Parámetros de configuración

| Argumento                   | Descripción                                                                                                                                                                                                 | Parámetro predeterminado                     | Sobre nombre                   |
| -------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------- | --------------------------- |
| --host                     | Establecer el host para vincular el servidor to                                                                                                                                                                              | `127.0.0.1`                           | LT_HOST                     |
| --port                     | Establecer el puerto al que se vinculará el servidor                                                                                                                                                                              | `5000`                                | LT_PORT                     |
| --char-limit               | Establecer límite de caracteres                                                                                                                                                                                         | `Sin Limite`                            | LT_CHAR_LIMIT               |
| --req-limit                | Establecer el número máximo de solicitudes por minuto por cliente (fuera de los límites establecidos por las claves API)                                                                                                                   | `Sin Limite`                            | LT_REQ_LIMIT                |
| --req-limit-storage        | URI de almacenamiento para limitar el almacenamiento de datos de solicitudes. Ver [Flask Limiter](https://flask-limiter.readthedocs.io/en/stable/configuration.html)                                                                   | `memoria://`                           | LT_REQ_LIMIT_STORAGE        |
| --req-time-cost            | Considera el coste de tiempo (en segundos) para limitar las solicitudes. Si una solicitud tarda 10 segundos y este valor se establece en 5, el coste de la solicitud es 2 o el coste real de la solicitud (el que sea mayor). | `Sin costo de tiempo`                        | LT_REQ_TIME_COST            |
| --batch-limit              | Establecer el número máximo de textos a traducir en una solicitud por lotes                                                                                                                                                 | `Sin Limite`                            | LT_BATCH_LIMIT              |
| --frontend-language-source | Establecer el idioma predeterminado del frontend - fuente                                                                                                                                                                      | `auto`                                | LT_FRONTEND_LANGUAGE_SOURCE |
| --frontend-language-target | Establecer el idioma predeterminado del frontend - objetivo                                                                                                                                                                      | `locale` (coincide con la configuración regional del sitio)        | LT_FRONTEND_LANGUAGE_TARGET |
| --frontend-timeout         | Establecer el tiempo de espera de traducción del frontend                                                                                                                                                                            | `500`                                 | LT_FRONTEND_TIMEOUT         |
| --api-keys-db-path         | Utilice una ruta específica dentro del contenedor para la base de datos local. Puede ser absoluta o relativa.                                                                                                                | `db/api_keys.db`                      | LT_API_KEYS_DB_PATH         |
| --api-keys-remote          | Utilice este punto final remoto para consultar claves API válidas en lugar de utilizar la base de datos local                                                                                                                    | `Vacío (usa db local en su lugar)`        | LT_API_KEYS_REMOTE          |
| --get-api-key-link         | Mostrar un enlace en la interfaz de usuario donde dirigir a los usuarios para obtener una clave API                                                                                                                                              | `Vacío (no se muestra ningún enlace en la interfaz web)`     | LT_GET_API_KEY_LINK         |
| --shared-storage           | URI de almacenamiento compartido que se utilizará para compartir datos entre múltiples procesos (por ejemplo, al usar gunicorn)                                                                                                                         | `memoria://`                           | LT_SHARED_STORAGE           |
| --secondary                | Marque esta instancia como una instancia secundaria para evitar conflictos con el nodo principal en configuraciones de múltiples nodos                                                                                                    | `Nodo primario`                        | LT_SECONDARY                |
| --load-only                | Establecer idiomas disponibles                                                                                                                                                                                     | `Vacío (utilizar todo de argostranslate)` | LT_LOAD_ONLY                |
| --threads                  | Establecer número de subprocesos                                                                                                                                                                                       | `4`                                   | LT_THREADS                  |
| --metrics-auth-token       | Proteja el punto final /metrics permitiendo solo clientes que tengan un token de portador de autorización válido                                                                                                         | `Vacío (no se requiere autenticación)`            | LT_METRICS_AUTH_TOKEN       |
| --url-prefix               | Agregar prefijo a la URL: ejemplo.com:5000/prefijo-url/                                                                                                                                                             | `/`                                   | LT_URL_PREFIX               |

### Notas:

- Cada argumento tiene una variable de entorno equivalente que puede usarse en su lugar. Las variables de entorno sobrescriben los valores predeterminados, pero tienen menor prioridad que los argumentos del comando y son especialmente útiles si se usan con Docker. Los nombres de las variables de entorno son la versión en mayúsculas del nombre del argumento del comando equivalente, con el prefijo `LT`.

- Para configurar el requisito de uso de la clave API, establezca `--req-limit` en `0` y agregue el indicador `--api-keys`. Las solicitudes realizadas sin una clave API correcta serán rechazadas.

- Al establecer `--update-models`, se actualizarán los modelos independientemente de si hay actualizaciones disponibles.

## Actualización

### Software

Si instaló con pip:

`pip install -U libretranslate`

Si usa docker:

`docker pull libretranslate/libretranslate`

### Modelos de lenguaje

Inicie el programa con el argumento `--update-models`. Por ejemplo: `libretranslate --update-models` o `./run.sh --update-models`.

También puede ejecutar el script `scripts/install_models.py`.

## Ejecutar con WSGI y Gunicorn

```bash
pip install gunicorn
gunicorn --bind 0.0.0.0:5000 'wsgi:app'
```

Puedes pasar los argumentos de la aplicación directamente a Gunicorn mediante:

```bash
gunicorn --bind 0.0.0.0:5000 'wsgi:app(api_keys=True)'
```

## Implementación de Kubernetes

Consulta el [artículo Mediano de JM Robles](https://jmrobles.medium.com/libretranslate-your-own-translation-service-on-kubernetes-b46c3e1af630) y el [k8s.yaml](https://github.com/LibreTranslate/LibreTranslate/blob/main/k8s.yaml) mejorado por @rasos.

### Gráfico de Helm

Gracias al trabajo de @rasos, ahora puedes instalar LibreTranslate en Kubernetes usando Helm.

Ya hay un gráfico de Helm disponible en el repositorio [helm-chart](https://github.com/LibreTranslate/helm-chart/), donde puedes encontrar más detalles.

Puede instalar rápidamente LibreTranslate en Kubernetes usando Helm con el siguiente comando:

```bash
helm repo add libretranslate https://libretranslate.github.io/helm-chart/
helm repo update
helm search repo libretranslate

helm install libretranslate libretranslate/libretranslate --namespace libretranslate --create-namespace
```

## Administrar claves API

LibreTranslate admite cuotas límite por usuario. Por ejemplo, puede emitir claves API a los usuarios para que puedan disfrutar de mayores límites de solicitudes por minuto (si también configura `--req-limit`). De forma predeterminada, todos los usuarios tienen un límite de velocidad basado en `--req-limit`, pero al pasar un parámetro opcional `api_key` a los endpoints REST, un usuario puede disfrutar de mayores límites de solicitudes. También puede especificar diferentes límites de caracteres que omiten el valor predeterminado `--char-limit` por clave.

Para usar claves API, simplemente inicie LibreTranslate con la opción `--api-keys`. Si modificó la ruta de la base de datos de claves API con la opción `--api-keys-db-path`, debe especificar la ruta con el mismo indicador de argumento al usar el comando `ltmanage keys`.

### Agregar nuevas claves

Para emitir una nueva clave API con un límite de 120 solicitudes por minuto:

```bash
ltmanage keys add 120
```

Para emitir una nueva clave API con 120 solicitudes por minuto y un máximo de 5000 caracteres por solicitud:

```bash
ltmanage keys add 120 --char-limit 5000
```

Si cambió la ruta de la base de datos de claves API:

```bash
ltmanage keys --api-keys-db-path path/to/db/dbName.db add 120
```

### Eliminar claves

```bash
ltmanage keys remove <api-key>
```

### Ver claves

```bash
ltmanage keys
```

## Métricas de Prometheus

LibreTranslate tiene Prometheus Capacidades de [exportador](https://prometheus.io/docs/instrumenting/exporters/) cuando pasa el argumento `--metrics` al inicio (deshabilitado de manera predeterminada). Cuando las métricas están habilitadas, se monta un punto final `/metrics` en la instancia:

<http://localhost:5000/metrics>

```promql
# HELP libretranslate_http_requests_in_flight Métrica multiproceso
# TYPE libretranslate_http_requests_in_flight Indicador
libretranslate_http_requests_in_flight{api_key="",endpoint="/translate",request_ip="127.0.0.1"} 0.0
# HELP libretranslate_http_request_duration_seconds Métrica multiproceso
# TYPE libretranslate_http_request_duration_seconds Resumen
libretranslate_http_request_duration_seconds_count{api_key="",endpoint="/translate",request_ip="127.0.0.1",status="200"} 0.0
libretranslate_http_request_duration_seconds_sum{api_key="",endpoint="/translate",request_ip="127.0.0.1",status="200"} 0.0
```

Puede configurar `prometheus.yml` para leer las métricas:

```yaml
scrape_configs:
- job_name: "libretranslate"

# Solo es necesario si usas --metrics-auth-token
#authorization:
#credentials: "mytoken"

static_configs:
- targets: ["localhost:5000"]
```

Para proteger el endpoint `/metrics`, también puedes usar `--metrics-auth-token mytoken`.

Si usa Gunicorn, asegúrese de crear un directorio para almacenar las métricas de datos multiproceso y configure `PROMETHEUS_MULTIPROC_DIR`:

```bash
mkdir -p /tmp/prometheus_data
rm /tmp/prometheus_data/*
export PROMETHEUS_MULTIPROC_DIR=/tmp/prometheus_data
gunicorn -c scripts/gunicorn_conf.py --bind 0.0.0.0:5000 'wsgi:app(metrics=True)'
```

## Enlaces de lenguaje

Puedes usar el [plugin oficial de traducción de Discourse](https://github.com/discourse/discourse-translator) para traducir temas de Discourse con LibreTranslate. Para instalarlo, simplemente modifica `/var/discourse/containers/app.yml`:

```yaml
## Los plugins van aquí
## Consulta https://meta.discourse.org/t/19157 para más detalles
hooks:
after_code:
- exec:
cd: $home/plugins
cmd:
- git clone https://github.com/discourse/docker_manager.git
- git clone https://github.com/discourse/discourse-translator
...
```

Luego, ejecuta `./launcher rebuild app`. Desde el panel de administración de Discourse, selecciona "LibreTranslate" como proveedor de traducción y configura los endpoints correspondientes.

Véalo en acción en esta [página](https://community.libretranslate.com/t/have-you-considered-adding-the-libretranslate-discourse-translator-multilingual-to-this-forum/766).

## Aplicaciones móviles

- [LibreTranslator](https://codeberg.org/BeoCode/LibreTranslator) es una aplicación para Android [disponible en Play Store](https://play.google.com/store/apps/details?id=de.beowulf.libretranslater) y [en la tienda de F-Droid](https://f-droid.org/packages/de.beowulf.libretranslater/) que utiliza la API de LibreTranslate.
- [Translate You](https://github.com/you-apps/TranslateYou) es una aplicación de traducción centrada en la privacidad, desarrollada con MD3, disponible [en la tienda de F-Droid](https://f-droid.org/packages/com.bnyro.translate/) y que utiliza la API de LibreTranslate, entre otros proveedores. - [LiTranslate](https://github.com/viktorkalyniuk/LiTranslate-iOS) es una aplicación para iOS [disponible en la App Store](https://apps.apple.com/us/app/litranslate/id1644385339) que utiliza la API de LibreTranslate.

## Navegador web

- [minbrowser](https://minbrowser.org/) es un navegador web con [soporte integrado para LibreTranslate](https://github.com/argosopentech/argos-translate/discussions/158#discussioncomment-1141551).
- Un complemento de LibreTranslate para Firefox está [actualmente en desarrollo](https://github.com/LibreTranslate/LibreTranslate/issues/55).

## Espejos

Esta es una lista de instancias públicas de LibreTranslate; algunas requieren una clave API. Si desea agregar una nueva URL, abra una solicitud de extracción.


| URL                                                         | Se requiere clave API   | Enlaces                                                                                                        |
| ----------------------------------------------------------- | ------------------ | ------------------------------------------------------------------------------------------------------------- |
| [libretranslate.com](https://libretranslate.com)            | :heavy_check_mark: | [ [Get API Key](https://portal.libretranslate.com) ] [ [Service Status](https://status.libretranslate.com/) ] |
| [translate.flossboxin.org.in](https://translate.flossboxin.org.in/) |  | [ [Contact/eMail](mailto:dev@flossboxin.org.in) ] |
| [lt.blitzw.in](https://lt.blitzw.in/) |  |  |

## TOR/i2p Espejos

| URL                                                                                                                                            |
| ---------------------------------------------------------------------------------------------------------------------------------------------- |
| [lt.vernccvbvyi5qhfzyqengccj7lkove6bjot2xhh5kajhwvidqafczrad.onion](http://lt.vernccvbvyi5qhfzyqengccj7lkove6bjot2xhh5kajhwvidqafczrad.onion/) |
| [lt.vern.i2p](http://vernf45n7mxwqnp5riaax7p67pwcl7wcefdcnqqvim7ckdx4264a.b32.i2p/)                                                            |

## Añadiendo nuevos modelos de lenguaje

Tiene dos opciones para crear nuevos modelos de lenguaje:

- [Locomotive](https://github.com/LibreTranslate/Locomotive)
- [Argos Train](https://github.com/argosopentech/argos-train) ([videotutorial](https://www.youtube.com/watch?v=Vj_qgnhOEwg))

La mayoría de los datos de entrenamiento provienen de [Opus](http://opus.nlpl.eu/), un corpus paralelo de código abierto. Consulte también [NLLU](https://nllu.libretranslate.com)

## Localización

La interfaz web de LibreTranslate está disponible en todos los idiomas a los que LibreTranslate puede traducir. También puede (aproximadamente) [traducirse a sí mismo!](https://github.com/LibreTranslate/LibreTranslate/blob/main/scripts/update_locales.py). Es posible que algunos idiomas no aparezcan en la interfaz de usuario, ya que aún no han sido revisados ​​por un usuario. Puedes habilitar todos los idiomas activando el modo `--debug`.

Para ayudar a mejorar o revisar las traducciones de la interfaz de usuario:

- Ve a <https://hosted.weblate.org/projects/libretranslate/app/#translations>. Todos los cambios se envían automáticamente a este repositorio.
- Una vez revisadas/editadas todas las cadenas, abre una solicitud de extracción y modifica `libretranslate/locales/{code}/meta.json`:

```json
{
"name": "<Idioma>",
"reviewed": true <-- Cambia esto de falso a verdadero
}
```


| Idioma              | Revisado           | Enlace de Pizarra web                                                              |
| --------------------- | ------------------ | ------------------------------------------------------------------------ |
| Arabic                |                    | [Edit](https://hosted.weblate.org/translate/libretranslate/app/ar/)      |
| Azerbaijani           |                    | [Edit](https://hosted.weblate.org/translate/libretranslate/app/az/)      |
| Basque                | :heavy_check_mark: | [Edit](https://hosted.weblate.org/translate/libretranslate/app/eu/)      |
| Chinese               | :heavy_check_mark: | [Edit](https://hosted.weblate.org/translate/libretranslate/app/zh/)      |
| Chinese (Traditional) |                    | [Edit](https://hosted.weblate.org/translate/libretranslate/app/zh_Hant/) |
| Czech                 | :heavy_check_mark: | [Edit](https://hosted.weblate.org/translate/libretranslate/app/cs/)      |
| Danish                |                    | [Edit](https://hosted.weblate.org/translate/libretranslate/app/da/)      |
| Dutch                 |                    | [Edit](https://hosted.weblate.org/translate/libretranslate/app/nl/)      |
| English               | :heavy_check_mark: | [Edit](https://hosted.weblate.org/projects/libretranslate/app/)          |
| Esperanto             | :heavy_check_mark: | [Edit](https://hosted.weblate.org/translate/libretranslate/app/eo/)      |
| Finnish               |                    | [Edit](https://hosted.weblate.org/translate/libretranslate/app/fi/)      |
| French                | :heavy_check_mark: | [Edit](https://hosted.weblate.org/translate/libretranslate/app/fr/)      |
| German                | :heavy_check_mark: | [Edit](https://hosted.weblate.org/translate/libretranslate/app/de/)      |
| Greek                 |                    | [Edit](https://hosted.weblate.org/translate/libretranslate/app/el/)      |
| Hebrew                |                    | [Edit](https://hosted.weblate.org/translate/libretranslate/app/he/)      |
| Hindi                 |                    | [Edit](https://hosted.weblate.org/translate/libretranslate/app/hi/)      |
| Hungarian             |                    | [Edit](https://hosted.weblate.org/translate/libretranslate/app/hu/)      |
| Indonesian            |                    | [Edit](https://hosted.weblate.org/translate/libretranslate/app/id/)      |
| Irish                 |                    | [Edit](https://hosted.weblate.org/translate/libretranslate/app/ga/)      |
| Italian               | :heavy_check_mark: | [Edit](https://hosted.weblate.org/translate/libretranslate/app/it/)      |
| Japanese              |                    | [Edit](https://hosted.weblate.org/translate/libretranslate/app/ja/)      |
| Kabyle                | :heavy_check_mark: | [Edit](https://hosted.weblate.org/projects/libretranslate/app/kab/)      |
| Korean                | :heavy_check_mark: | [Edit](https://hosted.weblate.org/translate/libretranslate/app/ko/)      |
| Occitan               |                    | [Edit](https://hosted.weblate.org/translate/libretranslate/app/oc/)      |
| Persian               |                    | [Edit](https://hosted.weblate.org/translate/libretranslate/app/fa/)      |
| Polish                |                    | [Edit](https://hosted.weblate.org/translate/libretranslate/app/pl/)      |
| Portuguese            | :heavy_check_mark: | [Edit](https://hosted.weblate.org/translate/libretranslate/app/pt/)      |
| Russian               | :heavy_check_mark: | [Edit](https://hosted.weblate.org/translate/libretranslate/app/ru/)      |
| Slovak                |                    | [Edit](https://hosted.weblate.org/translate/libretranslate/app/sk/)      |
| Spanish               | :heavy_check_mark: | [Edit](https://hosted.weblate.org/translate/libretranslate/app/es/)      |
| Swedish               |                    | [Edit](https://hosted.weblate.org/translate/libretranslate/app/sv/)      |
| Turkish               |                    | [Edit](https://hosted.weblate.org/translate/libretranslate/app/tr/)      |
| Ukrainian             | :heavy_check_mark: | [Edit](https://hosted.weblate.org/translate/libretranslate/app/uk/)      |
| Vietnamese            |                    | [Edit](https://hosted.weblate.org/translate/libretranslate/app/vi/)      |

## Mapa de ruta

Ayúdanos abriendo una solicitud de extracción!

- [ ] Enlaces de lenguaje para cada lenguaje de programación
- [ ] [Traducciones mejoradas](https://community.libretranslate.com/t/the-best-way-to-train-models/172)

Cualquier otra idea es bienvenida.

## Preguntas frecuentes

### Puedo usar su servidor API en libretranslate.com para mi aplicación en producción?

En resumen, sí, [pero solo si compras una clave API](https://portal.libretranslate.com). Por supuesto, siempre puedes ejecutar LibreTranslate gratis en tu propio servidor.

### Algunas traducciones en libretranslate.com son diferentes a las alojadas por el usuario. Por qué?

Por defecto, los modelos de lenguaje se cargan desde el [argos-index](https://github.com/argosopentech/argospm-index). A veces implementamos modelos en libretranslate.com que aún no se han añadido al índice argos, como los convertidos desde OPUS ([thread](https://community.libretranslate.com/t/opus-mt-language-models-port-thread/757))

### Dónde se guardan los modelos de lenguaje?

En `$HOME/.local/share/argos-translate/packages`. En Windows, es `C:\Users\youruser\.local\share\argos-translate\packages`.

### Puedo usar LibreTranslate tras un proxy inverso, como Apache2 o Caddy?

Sí, aquí hay ejemplos de configuración para Apache2 y Caddy que redirigen un subdominio (con certificado HTTPS) a LibreTranslate ejecutándose en un contenedor en el host local.

```bash
sudo docker run -ti --rm -p 127.0.0.1:5000:5000 libretranslate/libretranslate
```

Puede eliminar `127.0.0.1` del comando anterior si desea acceder a él desde `domain.tld:5000`, además de `subdomain.domain.tld` (esto puede ser útil para determinar si hay un problema con Apache 2 o el contenedor de Docker).

Agregue `--restart unless-stopped` si desea que este contenedor se inicie al arrancar, a menos que se detenga manualmente.

<details>
<summary>Configuración de Apache</summary>
<br>

Reemplace [YOUR_DOMAIN] con su dominio completo; por ejemplo, `translate.domain.tld` o `libretranslate.domain.tld`.

Elimine `#` en las líneas ErrorLog y CustomLog para registrar las solicitudes.

```ApacheConf
#Libretranslate

#Redireccionar http a https
<VirtualHost *:80>
Nombre del servidor http://[SU_DOMINIO]
Redirigir / https://[SU_DOMINIO]
# Registro de errores ${APACHE_LOG_DIR}/error.log
# Registro personalizado ${APACHE_LOG_DIR}/tr-access.log combinado
</VirtualHost>

#https
<HostVirtual *:443>
NombreDeServidor https://[SU_DOMINIO]

PassProxy / http://127.0.0.1:5000/
PassReverseProxy / http://127.0.0.1:5000/
ProxyPreserveHost Activado

SSLEngine Activado
ArchivoDeCertificadoSSL /etc/letsencrypt/live/[SU_DOMINIO]/fullchain.pem
ArchivoDeClaveDeCertificadoSSL /etc/letsencrypt/live/[SU_DOMINIO]/privkey.pem
ArchivoDeCadenaDeCertificadoSSL /etc/letsencrypt/live/[SU_DOMINIO]/fullchain.pem

# RegistroDeErrores ${APACHE_LOG_DIR}/tr-error.log
# RegistroPersonalizado ${APACHE_LOG_DIR}/tr-access.log Combinado
</VirtualHost>
```

Agregue esto a la configuración de un sitio existente o a un nuevo archivo en `/etc/apache2/sites-available/new-site.conf` y ejecute `sudo a2ensite new-site.conf`.

Para obtener un certificado de subdominio HTTPS, instale `certbot` (snap), ejecute `sudo certbot certonly --manual --preferred-challenges dns` e ingrese su información (con `subdomain.domain.tld` como dominio). Agregue un registro DNS TXT con su registrador de dominio cuando se le solicite. Esto guardará su certificado y clave en `/etc/letsencrypt/live/{subdomain.domain.tld}/`. Como alternativa, comente las líneas SSL si no desea usar HTTPS.

</details>

<details>
<summary>Configuración de Caddy</summary>
<br>

Reemplace [SU_DOMINIO] con su dominio completo; por ejemplo, `translate.domain.tld` o `libretranslate.domain.tld`.

```Caddyfile
#Libretranslate
[SU_DOMINIO] {
reverse_proxy localhost:5000
}
```

Agregue esto a un archivo Caddyfile existente o guárdelo como `Caddyfile` en cualquier directorio y ejecute `sudo caddy reload` en ese mismo directorio.

</details>

<details>
<summary>NGINX config</summary>
<br>

Reemplace [SU_DOMINIO] con su dominio completo; por ejemplo, `translate.domain.tld` o `libretranslate.domain.tld`.

Elimine `#` en las líneas `access_log` y `error_log` para deshabilitar el registro.

```NginxConf
server {
list 80; nombre_del_servidor [SU_DOMINIO];
return 301 https://$nombre_del_servidor$uri_de_solicitud;
}

servidor {
    list 443 http2 ssl;
    nombre_del_servidor [SU_DOMINIO];

    #registro_acceso off;
    #registro_error off;

    # Sección SSL
    certificado_ssl /etc/letsencrypt/live/[SU_DOMINIO]/fullchain.pem;
    clave_del_certificado_ssl /etc/letsencrypt/live/[SU_DOMINIO]/privkey.pem;

    protocolos_ssl TLSv1.2 TLSv1.3;

    # Utilizando el conjunto de cifrado recomendado de: https://wiki.mozilla.org/Security/Server_Side_TLS
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384';

    ssl_session_timeout 10m;
    ssl_session_cache shared:MozSSL:10m; # aproximadamente 40000 sesiones
    ssl_session_tickets off;

    # Especifica una curva para cifrados ECDHE.
    ssl_ecdh_curve prime256v1;
    # El servidor debe determinar los cifrados, no el cliente.
    ssl_prefer_server_ciphers on;

    # Sección de encabezado
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header Referrer-Policy "strict-origin" always;

    add_header X-Frame-Options "SAMEORIGIN" always; add_header X-XSS-Protection "1; modo=bloquear" siempre;
    add_header X-Content-Type-Options "nosniff" siempre;
    add_header X-Download-Options "noopen" siempre;
    add_header X-Robots-Tag "none" siempre;

    add_header Política de funciones "micrófono 'ninguno'; cámara 'ninguna'; geolocalización 'ninguna';" siempre;
    # Encabezado más reciente, pero no compatible en todas partes
    add_header Política de permisos "micrófono=(), cámara=(), geolocalización=()" siempre;

    # Eliminar X-Powered-By, que es una fuga de información
    fastcgi_hide_header X-Powered-By;

    # No enviar el encabezado del servidor nginx
    server_tokens off;

    # Sección GZIP
    gzip activado;
    gzip_disable "msie6";

    gzip_vary activado;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_buffers 16 8k;
    gzip_http_version 1.1;
    gzip_min_length 256; gzip_types texto/xml texto/javascript fuente/ttf fuente/eot fuente/otf aplicación/x-javascript aplicación/atom+xml aplicación/javascript aplicación/json aplicación/manifiesto+json aplicación/rss+xml aplicación/x-web-app-manifest+json aplicación/xhtml+xml aplicación/xml imagen/svg+xml imagen/x-icon texto/css texto/plain;


  location / {
      proxy_pass http://127.0.0.1:5000/;
      proxy_set_header Host $http_host;
      proxy_set_header X-Real-IP $remote_addr;
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      proxy_set_header X-Forwarded-Proto $scheme;
      client_max_body_size 0;
  }
}

```

Agregue esto a una configuración de NGINX existente o guárdelo como `libretranslate` en el directorio `/etc/nginx/site-enabled` y ejecute `sudo nginx -s reload`.

</details>

### Puedo ejecutarlo como systemd (el instalado por defecto en pip/python)?

Sí, simplemente cree un archivo de servicio en `/etc/systemd/system` y habilítelo para que se ejecute al inicio.
El archivo .env (entorno) es opcional según su configuración. Agregue lo siguiente al archivo (modifique los valores según sea necesario) y nómbrelo "libretranslate.service).

```javascript
[Unidad]
Descripción=LibreTranslate
Después=network.target
[Servicio]
Usuario=root
Tipo=idle
Reiniciar=always
Environment="PATH=/usr/local/lib/python3.11/dist-packages/libretranslate"
ExecStart=/usr/bin/python3 /usr/local/bin/libretranslate
EnvironmentFile=/usr/local/lib/python3.11/dist-packages/libretranslate/.env
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=1
[Instalar]
WantedBy=multi-user.target
```

Una vez guardado, vuelva a cargar el archivo Daemon e iniciar el servicio:

```javascript
systemctl daemon-reload
systemctl start libretranslate.service
systemctl enable libretranslate.service
```

### Puedo realizar traducciones por lotes?

Sí, pasa un array de cadenas en lugar de una cadena al campo `q`:

```javascript
const res = await fetch("https://libretranslate.com/translate", {
method: "POST",
body: JSON.stringify({
q: ["Hello", "world"],
source: "en",
target: "es",
}),
headers: { "Content-Type": "application/json" },
});

console.log(await res.json());
// {
// "translatedText": [
// "Hola",
// "mundo"
// ]
// }
```

## Contribuyendo

Agradecemos sus contribuciones! Aquí tienen algunas ideas:

- Entrenar un nuevo modelo de lenguaje usando [Locomotive](https://github.com/LibreTranslate/Locomotive). Por ejemplo, queremos entrenar redes neuronales mejoradas para [alemán](https://community.libretranslate.com/t/help-wanted-improve-en-de-translation/935) y muchos otros idiomas.
- Puedes superar el rendimiento de nuestros modelos de lenguaje? Entrena uno nuevo y comparémoslo. Para enviar tu modelo, publica en el [foro de la comunidad](https://community.libretranslate.com/) un enlace para descargar tu archivo .argosmodel y un texto de muestra que tu modelo haya traducido.
- Elige un [problema](https://github.com/LibreTranslate/LibreTranslate/issues) en el que trabajar.

## Créditos

Este trabajo es posible en gran medida gracias a [Argos Translate](https://github.com/argosopentech/argos-translate), que impulsa el motor de traducción.

## Licencia

[Licencia Pública General GNU Affero v3](https://www.gnu.org/licenses/agpl-3.0.en.html)

## Marca registrada

Consulte las [Directrices de marca registrada](https://github.com/LibreTranslate/LibreTranslate/blob/main/docs/TRADEMARK.es.md)

## Projectos Relacionados

* [LTEngine](https://github.com/LibreTranslate/LTEngine): Machine translation powered by LLMs with a LibreTranslate-compatible API

## Otros idiomas

- [English (README)](/README.md)