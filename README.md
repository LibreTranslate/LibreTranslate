# LibreTranslate

[Try it online!](https://libretranslate.com) | [API Docs](https://libretranslate.com/docs) | [Community Forum](https://community.libretranslate.com/)

[![Python versions](https://img.shields.io/pypi/pyversions/libretranslate)](https://pypi.org/project/libretranslate) [![Run tests](https://github.com/LibreTranslate/LibreTranslate/workflows/Run%20tests/badge.svg)](https://github.com/LibreTranslate/LibreTranslate/actions?query=workflow%3A%22Run+tests%22) [![Build and Publish Docker Image](https://github.com/LibreTranslate/LibreTranslate/actions/workflows/publish-docker.yml/badge.svg)](https://github.com/LibreTranslate/LibreTranslate/actions/workflows/publish-docker.yml) [![Publish package](https://github.com/LibreTranslate/LibreTranslate/actions/workflows/publish-package.yml/badge.svg)](https://github.com/LibreTranslate/LibreTranslate/actions/workflows/publish-package.yml) [![Awesome Humane Tech](https://raw.githubusercontent.com/humanetech-community/awesome-humane-tech/main/humane-tech-badge.svg?sanitize=true)](https://codeberg.org/teaserbot-labs/delightful-humane-design)

Free and Open Source Machine Translation API, entirely self-hosted. Unlike other APIs, it doesn't rely on proprietary providers such as Google or Azure to perform translations. Instead, its translation engine is powered by the open source [Argos Translate](https://github.com/argosopentech/argos-translate) library.

![image](https://user-images.githubusercontent.com/64697405/139015751-279f31ac-36f1-4950-9ea7-87e76bf65f51.png)

[Try it online!](https://libretranslate.com) | [API Docs](https://libretranslate.com/docs)

## API Examples

### Simple

Request:

```javascript
const res = await fetch("https://libretranslate.com/translate", {
  method: "POST",
  body: JSON.stringify({
    q: "Hello!",
    source: "en",
    target: "es"
  }),
  headers: { "Content-Type": "application/json" }
});

console.log(await res.json());
```

Response:

```javascript
{
    "translatedText": "¡Hola!"
}
```

### Auto Detect Language

Request:

```javascript
const res = await fetch("https://libretranslate.com/translate", {
  method: "POST",
  body: JSON.stringify({
    q: "Ciao!",
    source: "auto",
    target: "en"
  }),
  headers: { "Content-Type": "application/json" }
});

console.log(await res.json());
```

Response:

```javascript
{
    "detectedLanguage": {
        "confidence": 83,
        "language": "it"
    },
    "translatedText": "Bye!"
}
```

### HTML (beta)

Request:

```javascript
const res = await fetch("https://libretranslate.com/translate", {
  method: "POST",
  body: JSON.stringify({
    q: '<p class="green">Hello!</p>',
    source: "en",
    target: "es",
    format: "html"
  }),
  headers: { "Content-Type": "application/json" }
});

console.log(await res.json());
```

Response:

```javascript
{
    "translatedText": "<p class=\"green\">¡Hola!</p>"
}
```

## Install and Run

You can run your own API server with just a few lines of setup!

Make sure you have Python installed (3.8 or higher is recommended), then simply run:

```bash
pip install libretranslate
libretranslate [args]
```

Then open a web browser to <http://localhost:5000>

On Ubuntu 20.04 you can also use the install script available at <https://github.com/argosopentech/LibreTranslate-init>

## Run with Docker

You can also run the application with [docker](https://docker.com):

### Linux/macOS

```bash
./run.sh [args]
```

### Windows

```bash
run.bat [args]
```

## Build and Run

See [CONTIRBUTING.md](./CONTRIBUTING.md) for information on how to build and run the project yourself.

### CUDA

You can use hardware acceleration to speed up translations on a GPU machine with CUDA 11.2 and [nvidia-docker](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html) installed.

Run this version with:

```bash
docker compose -f docker-compose.cuda.yml up -d --build
```

## Arguments

Arguments passed to the process or set via environment variables are split into two kinds.

- Settings or runtime flags used to toggle specific runmodes or disable parts of the application. These act as toggle when added or removed.

- Configuration parameters to set various limits and configure the application. These require a parameter to be passed to function, if removed the default parameters are used.

### Settings / Flags

| Argument                    | Description                                                                                                 | Default Setting      | Env. name                    |
|-----------------------------|-------------------------------------------------------------------------------------------------------------| -------------------- |------------------------------|
| --debug                     | Enable debug environment                                                                                    | `Disabled`           | LT_DEBUG                     |
| --ssl                       | Whether to enable SSL                                                                                       | `Disabled`               | LT_SSL                       |
| --api-keys                  | Enable API keys database for per-client rate limits when --req-limit is reached                             | `Don't use API keys` | LT_API_KEYS                  |
| --require-api-key-origin    | Require use of an API key for programmatic access to the API, unless the request origin matches this domain | `No restrictions on domain origin` | LT_REQUIRE_API_KEY_ORIGIN    |
| --require-api-key-secret    | Require use of an API key for programmatic access to the API, unless the client also sends a secret match   | `No secrets required` | LT_REQUIRE_API_KEY_SECRET    |
| --suggestions               | Allow user suggestions                                                                                      | `Disabled`    | LT_SUGGESTIONS               |
| --disable-files-translation | Disable files translation                                                                                   | `File translation allowed`    | LT_DISABLE_FILES_TRANSLATION |
| --disable-web-ui            | Disable web ui                                                                                              | `Web Ui enabled`    | LT_DISABLE_WEB_UI            |
| --update-models             | Update language models at startup                                                                           | `Only on if no models found`    | LT_UPDATE_MODELS            |
| --metrics                   | Enable the /metrics endpoint for exporting [Prometheus](https://prometheus.io/) usage metrics               | `Disabled`    | LT_METRICS            |

### Configuration Parameters

| Argument                   | Description                                                                                                                                                                                                 | Default Parameter                     | Env. name                   |
| -------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------- | --------------------------- |
| --host                     | Set host to bind the server to                                                                                                                                                                              | `127.0.0.1`                           | LT_HOST                     |
| --port                     | Set port to bind the server to                                                                                                                                                                              | `5000`                                | LT_PORT                     |
| --char-limit               | Set character limit                                                                                                                                                                                         | `No limit`                            | LT_CHAR_LIMIT               |
| --req-limit                | Set maximum number of requests per minute per client (outside of limits set by api keys)                                                                                                                    | `No limit`                            | LT_REQ_LIMIT                |
| --req-limit-storage        | Storage URI to use for request limit data storage. See [Flask Limiter](https://flask-limiter.readthedocs.io/en/stable/configuration.html)                                                                   | `memory://`                           | LT_REQ_LIMIT_STORAGE        |
| --req-time-cost            | Considers a time cost (in seconds) for request limiting purposes. If a request takes 10 seconds and this value is set to 5, the request cost is either 2 or the actual request cost (whichever is greater). | `No time cost`                        | LT_REQ_TIME_COST            |
| --batch-limit              | Set maximum number of texts to translate in a batch request                                                                                                                                                 | `No limit`                            | LT_BATCH_LIMIT              |
| --ga-id                    | Enable Google Analytics on the API client page by providing an ID                                                                                                                                           | `Empty (no tracking)`                 | LT_GA_ID                    |
| --frontend-language-source | Set frontend default language - source                                                                                                                                                                      | `auto`                                | LT_FRONTEND_LANGUAGE_SOURCE |
| --frontend-language-target | Set frontend default language - target                                                                                                                                                                      | `locale` (match site's locale)        | LT_FRONTEND_LANGUAGE_TARGET |
| --frontend-timeout         | Set frontend translation timeout                                                                                                                                                                            | `500`                                 | LT_FRONTEND_TIMEOUT         |
| --api-keys-db-path         | Use a specific path inside the container for the local database. Can be absolute or relative                                                                                                                | `db/api_keys.db`                      | LT_API_KEYS_DB_PATH         |
| --api-keys-remote          | Use this remote endpoint to query for valid API keys instead of using the local database                                                                                                                    | `Empty (use local db instead)`        | LT_API_KEYS_REMOTE          |
| --get-api-key-link         | Show a link in the UI where to direct users to get an API key                                                                                                                                               | `Empty (no link shown on web ui)`     | LT_GET_API_KEY_LINK         |
| --shared-storage           | Shared storage URI to use for multi-process data sharing (e.g. when using gunicorn)                                                                                                                         | `memory://`                           | LT_SHARED_STORAGE           |
| --load-only                | Set available languages                                                                                                                                                                                     | `Empty (use all from argostranslate)` | LT_LOAD_ONLY                |
| --threads                  | Set number of threads                                                                                                                                                                                       | `4`                                   | LT_THREADS                  |
| --metrics-auth-token       | Protect the /metrics endpoint by allowing only clients that have a valid Authorization Bearer token                                                                                                         | `Empty (no auth required)`            | LT_METRICS_AUTH_TOKEN       |
| --url-prefix               | Add prefix to URL: example.com:5000/url-prefix/                                                                                                                                                             | `/`                                   | LT_URL_PREFIX               |

### Notes:

- Each argument has an equivalent environment variable that can be used instead. The env. variables overwrite the default values but have lower priority than the command arguments and are particularly useful if used with Docker. The environment variable names are the upper-snake-case of the equivalent command argument's name with a `LT` prefix.

- To configure requirement for api key to use, set `--req-limit` to `0` and add the `--api-keys` flag. Requests made without a proper api key will be rejected.

- Setting `--update-models` will update models regardless of whether updates are available or not.

## Update

### Software

If you installed with pip:

`pip install -U libretranslate`

If you're using docker:

`docker pull libretranslate/libretranslate`

### Language Models

Start the program with the `--update-models` argument. For example: `libretranslate --update-models` or `./run.sh --update-models`.

Alternatively you can also run the `scripts/install_models.py` script.

## Run with WSGI and Gunicorn

```bash
pip install gunicorn
gunicorn --bind 0.0.0.0:5000 'wsgi:app'
```

You can pass application arguments directly to Gunicorn via:

```bash
gunicorn --bind 0.0.0.0:5000 'wsgi:app(api_keys=True)'
```

## Kubernetes Deployment

See [Medium article by JM Robles](https://jmrobles.medium.com/libretranslate-your-own-translation-service-on-kubernetes-b46c3e1af630) and the improved [k8s.yaml](https://github.com/LibreTranslate/LibreTranslate/blob/main/k8s.yaml) by @rasos.

### Helm Chart

Based on @rasos work you can now install LibreTranslate on Kubernetes using Helm.

A Helm chart is now available in the [helm-chart](https://github.com/LibreTranslate/helm-chart/) repository where you can find more details.

You can quickly install LibreTranslate on Kubernetes using Helm with the following command:

```bash
helm repo add libretranslate https://libretranslate.github.io/helm-chart/
helm repo update
helm search repo libretranslate

helm install libretranslate libretranslate/libretranslate --namespace libretranslate --create-namespace
```

## Manage API Keys

LibreTranslate supports per-user limit quotas, e.g. you can issue API keys to users so that they can enjoy higher requests limits per minute (if you also set `--req-limit`). By default all users are rate-limited based on `--req-limit`, but passing an optional `api_key` parameter to the REST endpoints allows a user to enjoy higher request limits. You can also specify different character limits that bypass the default `--char-limit` value on a per-key basis.

To use API keys simply start LibreTranslate with the `--api-keys` option. If you modified the API keys database path with the option `--api-keys-db-path`, you must specify the path with the same argument flag when using the `ltmanage keys` command.

### Add New Keys

To issue a new API key with 120 requests per minute limits:

```bash
ltmanage keys add 120
```

To issue a new API key with 120 requests per minute and a maximum of 5,000 characters per request:

```bash
ltmanage keys add 120 --char-limit 5000
```

If you changed the API keys database path:

```bash
ltmanage keys --api-keys-db-path path/to/db/dbName.db add 120
```

### Remove Keys

```bash
ltmanage keys remove <api-key>
```

### View Keys

```bash
ltmanage keys
```

## Prometheus Metrics

LibreTranslate has Prometheus [exporter](https://prometheus.io/docs/instrumenting/exporters/) capabilities when you pass the `--metrics` argument at startup (disabled by default). When metrics are enabled, a `/metrics` endpoint is mounted on the instance:

<http://localhost:5000/metrics>

```promql
# HELP libretranslate_http_requests_in_flight Multiprocess metric
# TYPE libretranslate_http_requests_in_flight gauge
libretranslate_http_requests_in_flight{api_key="",endpoint="/translate",request_ip="127.0.0.1"} 0.0
# HELP libretranslate_http_request_duration_seconds Multiprocess metric
# TYPE libretranslate_http_request_duration_seconds summary
libretranslate_http_request_duration_seconds_count{api_key="",endpoint="/translate",request_ip="127.0.0.1",status="200"} 0.0
libretranslate_http_request_duration_seconds_sum{api_key="",endpoint="/translate",request_ip="127.0.0.1",status="200"} 0.0
```

You can then configure `prometheus.yml` to read the metrics:

```yaml
scrape_configs:
  - job_name: "libretranslate"

    # Needed only if you use --metrics-auth-token
    #authorization:
      #credentials: "mytoken"

    static_configs:
      - targets: ["localhost:5000"]
```

To secure the `/metrics` endpoint you can also use `--metrics-auth-token mytoken`.

If you use Gunicorn, make sure to create a directory for storing multiprocess data metrics and set `PROMETHEUS_MULTIPROC_DIR`:

```bash
mkdir -p /tmp/prometheus_data
rm /tmp/prometheus_data/*
export PROMETHEUS_MULTIPROC_DIR=/tmp/prometheus_data
gunicorn -c scripts/gunicorn_conf.py --bind 0.0.0.0:5000 'wsgi:app(metrics=True)'
```

## Language Bindings

You can use the LibreTranslate API using the following bindings:

- Rust: <https://github.com/DefunctLizard/libretranslate-rs>
- Node.js: <https://github.com/franciscop/translate>
- TypeScript: <https://github.com/tderflinger/libretranslate-ts>
- .Net: <https://github.com/sigaloid/LibreTranslate.Net>
- Go: <https://github.com/SnakeSel/libretranslate>
- Python: <https://github.com/argosopentech/LibreTranslate-py>
- PHP: <https://github.com/jefs42/libretranslate>
- C++: <https://github.com/argosopentech/LibreTranslate-cpp>
- Swift: <https://github.com/wacumov/libretranslate>
- Unix: <https://github.com/argosopentech/LibreTranslate-sh>
- Shell: <https://github.com/Hayao0819/Hayao-Tools/tree/master/libretranslate-sh>
- Java: <https://github.com/suuft/libretranslate-java>
- Ruby: <https://github.com/noesya/libretranslate>
- R: <https://github.com/myanesp/libretranslateR>

## Discourse Plugin

You can use the [official discourse translator plugin](https://github.com/discourse/discourse-translator) to translate [Discourse](https://discourse.org) topics with LibreTranslate. To install it simply modify `/var/discourse/containers/app.yml`:

```yaml
## Plugins go here
## see https://meta.discourse.org/t/19157 for details
hooks:
  after_code:
    - exec:
        cd: $home/plugins
        cmd:
          - git clone https://github.com/discourse/docker_manager.git
          - git clone https://github.com/discourse/discourse-translator
    ...
```

Then issue `./launcher rebuild app`. From the Discourse's admin panel then select "LibreTranslate" as a translation provider and set the relevant endpoint configurations.

See it in action on this [page](https://community.libretranslate.com/t/have-you-considered-adding-the-libretranslate-discourse-translator-multilingual-to-this-forum/766).

## Mobile Apps

- [LibreTranslator](https://codeberg.org/BeoCode/LibreTranslator) is an Android app [available on the Play Store](https://play.google.com/store/apps/details?id=de.beowulf.libretranslater) and [in the F-Droid store](https://f-droid.org/packages/de.beowulf.libretranslater/) that uses the LibreTranslate API.
- [LiTranslate](https://github.com/viktorkalyniuk/LiTranslate-iOS) is an iOS app [available on the App Store](https://apps.apple.com/us/app/litranslate/id1644385339) that uses the LibreTranslate API.

## Web browser

- [minbrowser](https://minbrowser.org/) is a web browser with [integrated LibreTranslate support](https://github.com/argosopentech/argos-translate/discussions/158#discussioncomment-1141551).
- A LibreTranslate Firefox addon is [currently a work in progress](https://github.com/LibreTranslate/LibreTranslate/issues/55).

## Mirrors

This is a list of public LibreTranslate instances, some require an API key. If you want to add a new URL, please open a pull request.

URL |API Key Required | Links
--- | --- | ---
[libretranslate.com](https://libretranslate.com)|:heavy_check_mark:|[ [Get API Key](https://portal.libretranslate.com) ] [ [Service Status](https://status.libretranslate.com/) ]
[translate.terraprint.co](https://translate.terraprint.co/)|-
[trans.zillyhuhn.com](https://trans.zillyhuhn.com/)|-
[libretranslate.eownerdead.dedyn.io](https://libretranslate.eownerdead.dedyn.io)|-

## TOR/i2p Mirrors

URL |
--- |
[lt.vernccvbvyi5qhfzyqengccj7lkove6bjot2xhh5kajhwvidqafczrad.onion](http://lt.vernccvbvyi5qhfzyqengccj7lkove6bjot2xhh5kajhwvidqafczrad.onion/)|
[lt.vern.i2p](http://vernf45n7mxwqnp5riaax7p67pwcl7wcefdcnqqvim7ckdx4264a.b32.i2p/)|

## Adding New Language Models

You have two options to create new language models:
 * [Locomotive](https://github.com/LibreTranslate/Locomotive)
 * [Argos Train](https://github.com/argosopentech/argos-train) ([video tutorial](https://www.youtube.com/watch?v=Vj_qgnhOEwg))

Most of the training data is from [Opus](http://opus.nlpl.eu/), which is an open source parallel corpus. Check also [NLLU](https://nllu.libretranslate.com)

## Localization

The LibreTranslate Web UI is available in all the languages for which LibreTranslate can translate to. It can also (roughly) [translate itself!](https://github.com/LibreTranslate/LibreTranslate/blob/main/scripts/update_locales.py) Some languages might not appear in the UI since they haven't been reviewed by a human yet. You can enable all languages by turning on `--debug` mode.

To help improve or review the UI translations:

- Go to <https://hosted.weblate.org/projects/libretranslate/app/#translations>. All changes are automatically pushed to this repository.
- Once all strings have been reviewed/edited, open a pull request and change `libretranslate/locales/{code}/meta.json`:

 ```json
{
  "name": "<Language>",
  "reviewed": true <-- Change this from false to true
}
 ```

### UI Languages

Language | Reviewed | Weblate Link
-------- | -------- | ------------
Arabic |  | [Edit](https://hosted.weblate.org/translate/libretranslate/app/ar/)
Azerbaijani |  | [Edit](https://hosted.weblate.org/translate/libretranslate/app/az/)
Chinese |  | [Edit](https://hosted.weblate.org/translate/libretranslate/app/zh/)
Chinese (Traditional) |  | [Edit](https://hosted.weblate.org/translate/libretranslate/app/zh_Hant/)
Czech | :heavy_check_mark: | [Edit](https://hosted.weblate.org/translate/libretranslate/app/cs/)
Danish |  | [Edit](https://hosted.weblate.org/translate/libretranslate/app/da/)
Dutch |  | [Edit](https://hosted.weblate.org/translate/libretranslate/app/nl/)
English | :heavy_check_mark: | [Edit](https://hosted.weblate.org/projects/libretranslate/app/)
Esperanto | :heavy_check_mark: | [Edit](https://hosted.weblate.org/translate/libretranslate/app/eo/)
Finnish |  | [Edit](https://hosted.weblate.org/translate/libretranslate/app/fi/)
French | :heavy_check_mark: | [Edit](https://hosted.weblate.org/translate/libretranslate/app/fr/)
German | :heavy_check_mark: | [Edit](https://hosted.weblate.org/translate/libretranslate/app/de/)
Greek |  | [Edit](https://hosted.weblate.org/translate/libretranslate/app/el/)
Hebrew |  | [Edit](https://hosted.weblate.org/translate/libretranslate/app/he/)
Hindi |  | [Edit](https://hosted.weblate.org/translate/libretranslate/app/hi/)
Hungarian |  | [Edit](https://hosted.weblate.org/translate/libretranslate/app/hu/)
Indonesian |  | [Edit](https://hosted.weblate.org/translate/libretranslate/app/id/)
Irish |  | [Edit](https://hosted.weblate.org/translate/libretranslate/app/ga/)
Italian | :heavy_check_mark: | [Edit](https://hosted.weblate.org/translate/libretranslate/app/it/)
Japanese |  | [Edit](https://hosted.weblate.org/translate/libretranslate/app/ja/)
Kabyle |  | [Edit](https://hosted.weblate.org/projects/libretranslate/app/kab/)
Korean | :heavy_check_mark: | [Edit](https://hosted.weblate.org/translate/libretranslate/app/ko/)
Occitan |  | [Edit](https://hosted.weblate.org/translate/libretranslate/app/oc/)
Persian |  | [Edit](https://hosted.weblate.org/translate/libretranslate/app/fa/)
Polish |  | [Edit](https://hosted.weblate.org/translate/libretranslate/app/pl/)
Portuguese | :heavy_check_mark: | [Edit](https://hosted.weblate.org/translate/libretranslate/app/pt/)
Russian | :heavy_check_mark: | [Edit](https://hosted.weblate.org/translate/libretranslate/app/ru/)
Slovak |  | [Edit](https://hosted.weblate.org/translate/libretranslate/app/sk/)
Spanish | :heavy_check_mark: | [Edit](https://hosted.weblate.org/translate/libretranslate/app/es/)
Swedish |  | [Edit](https://hosted.weblate.org/translate/libretranslate/app/sv/)
Turkish |  | [Edit](https://hosted.weblate.org/translate/libretranslate/app/tr/)
Ukranian | :heavy_check_mark: | [Edit](https://hosted.weblate.org/translate/libretranslate/app/uk/)
Vietnamese |  | [Edit](https://hosted.weblate.org/translate/libretranslate/app/vi/)

## Roadmap

Help us by opening a pull request!

- [ ] Language bindings for every computer language
- [ ] [Improved translations](https://community.libretranslate.com/t/the-best-way-to-train-models/172)

Any other idea is welcome also.

## FAQ

### Can I use your API server at libretranslate.com for my application in production?

In short, yes, [but only if you buy an API key](https://portal.libretranslate.com). You can always run LibreTranslate for free on your own server of course.

### Some translations on libretranslate.com are different than the self-hosted ones. Why?

By default language models are loaded from the [argos-index](https://github.com/argosopentech/argospm-index). Sometimes we deploy models on libretranslate.com that haven't been added to the argos-index yet, such as those converted from OPUS ([thread](https://community.libretranslate.com/t/opus-mt-language-models-port-thread/757))

### Where are the language models saved?

In `$HOME/.local/share/argos-translate/packages`. On Windows that's `C:\Users\youruser\.local\share\argos-translate\packages`.

### Can I use LibreTranslate behind a reverse proxy, like Apache2 or Caddy?

Yes, here are config examples for Apache2 and Caddy that redirect a subdomain (with HTTPS certificate) to LibreTranslate running on a docker at localhost.

```bash
sudo docker run -ti --rm -p 127.0.0.1:5000:5000 libretranslate/libretranslate
```

You can remove `127.0.0.1` on the above command if you want to be able to access it from `domain.tld:5000`, in addition to `subdomain.domain.tld` (this can be helpful to determine if there is an issue with Apache2 or the docker container).

Add `--restart unless-stopped` if you want this docker to start on boot, unless manually stopped.

<details>
<summary>Apache config</summary>
<br>

Replace [YOUR_DOMAIN] with your full domain; for example, `translate.domain.tld` or `libretranslate.domain.tld`.

Remove `#` on the ErrorLog and CustomLog lines to log requests.

```ApacheConf
#Libretranslate

#Redirect http to https
<VirtualHost *:80>
    ServerName http://[YOUR_DOMAIN]
    Redirect / https://[YOUR_DOMAIN]
    # ErrorLog ${APACHE_LOG_DIR}/error.log
    # CustomLog ${APACHE_LOG_DIR}/tr-access.log combined
 </VirtualHost>

#https
<VirtualHost *:443>
    ServerName https://[YOUR_DOMAIN]

    ProxyPass / http://127.0.0.1:5000/
    ProxyPassReverse / http://127.0.0.1:5000/
    ProxyPreserveHost On

    SSLEngine on
    SSLCertificateFile /etc/letsencrypt/live/[YOUR_DOMAIN]/fullchain.pem
    SSLCertificateKeyFile /etc/letsencrypt/live/[YOUR_DOMAIN]/privkey.pem
    SSLCertificateChainFile /etc/letsencrypt/live/[YOUR_DOMAIN]/fullchain.pem

    # ErrorLog ${APACHE_LOG_DIR}/tr-error.log
    # CustomLog ${APACHE_LOG_DIR}/tr-access.log combined
</VirtualHost>
```

Add this to an existing site config, or a new file in `/etc/apache2/sites-available/new-site.conf` and run `sudo a2ensite new-site.conf`.

To get a HTTPS subdomain certificate, install `certbot` (snap), run `sudo certbot certonly --manual --preferred-challenges dns` and enter your information (with `subdomain.domain.tld` as the domain). Add a DNS TXT record with your domain registrar when asked. This will save your certificate and key to `/etc/letsencrypt/live/{subdomain.domain.tld}/`. Alternatively, comment the SSL lines out if you don't want to use HTTPS.
</details>

<details>
<summary>Caddy config</summary>
<br>

Replace [YOUR_DOMAIN] with your full domain; for example, `translate.domain.tld` or `libretranslate.domain.tld`.

```Caddyfile
#Libretranslate
[YOUR_DOMAIN] {
  reverse_proxy localhost:5000
}
```

Add this to an existing Caddyfile or save it as `Caddyfile` in any directory and run `sudo caddy reload` in that same directory.

</details>

<details>
<summary>NGINX config</summary>
<br>

Replace [YOUR_DOMAIN] with your full domain; for example, `translate.domain.tld` or `libretranslate.domain.tld`.

Remove `#` on the `access_log` and `error_log` lines to disable logging.

```NginxConf
server {
  listen 80;
  server_name [YOUR_DOMAIN];
  return 301 https://$server_name$request_uri;
}

server {
  listen 443 http2 ssl;
  server_name [YOUR_DOMAIN];

  #access_log off;
  #error_log off;

  # SSL Section
  ssl_certificate /etc/letsencrypt/live/[YOUR_DOMAIN]/fullchain.pem;
  ssl_certificate_key /etc/letsencrypt/live/[YOUR_DOMAIN]/privkey.pem;

  ssl_protocols TLSv1.2 TLSv1.3;

  # Using the recommended cipher suite from: https://wiki.mozilla.org/Security/Server_Side_TLS
  ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384';

  ssl_session_timeout 10m;
  ssl_session_cache shared:MozSSL:10m;  # about 40000 sessions
  ssl_session_tickets off;

  # Specifies a curve for ECDHE ciphers.
  ssl_ecdh_curve prime256v1;
  # Server should determine the ciphers, not the client
  ssl_prefer_server_ciphers on;


  # Header section
  add_header Strict-Transport-Security  "max-age=31536000; includeSubDomains; preload" always;
  add_header Referrer-Policy            "strict-origin" always;

  add_header X-Frame-Options            "SAMEORIGIN"    always;
  add_header X-XSS-Protection           "1; mode=block" always;
  add_header X-Content-Type-Options     "nosniff"       always;
  add_header X-Download-Options         "noopen"        always;
  add_header X-Robots-Tag               "none"          always;

  add_header Feature-Policy             "microphone 'none'; camera 'none'; geolocation 'none';"  always;
  # Newer header but not everywhere supported
  add_header Permissions-Policy         "microphone=(), camera=(), geolocation=()" always;

  # Remove X-Powered-By, which is an information leak
  fastcgi_hide_header X-Powered-By;

  # Do not send nginx server header
  server_tokens off;

  # GZIP Section
  gzip on;
  gzip_disable "msie6";

  gzip_vary on;
  gzip_proxied any;
  gzip_comp_level 6;
  gzip_buffers 16 8k;
  gzip_http_version 1.1;
  gzip_min_length 256;
  gzip_types text/xml text/javascript font/ttf font/eot font/otf application/x-javascript application/atom+xml application/javascript application/json application/manifest+json application/rss+xml application/x-web-app-manifest+json application/xhtml+xml application/xml image/svg+xml image/x-icon text/css text/plain;

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

Add this to an existing NGINX config or save it as `libretranslate` in the `/etc/nginx/site-enabled` directory and run `sudo nginx -s reload`.

</details>

### Can I do batch translations?

Yes, pass an array of strings instead of a string to the `q` field:

```javascript
const res = await fetch("https://libretranslate.com/translate", {
  method: "POST",
  body: JSON.stringify({
    q: ["Hello", "world"],
    source: "en",
    target: "es"
  }),
  headers: { "Content-Type": "application/json" }
});

console.log(await res.json());
// {
//     "translatedText": [
//         "Hola",
//         "mundo"
//     ]
// }
```

## Contributing

We welcome contributions! Here's some ideas:

* Train a new language model using [Locomotive](https://github.com/LibreTranslate/Locomotive). For example, we want to train improved neural networks for [German](https://community.libretranslate.com/t/help-wanted-improve-en-de-translation/935) and many other languages.
* Can you beat the performance of our language models? Train a new one and let's compare it. To submit your model make a post on the [community forum](https://community.libretranslate.com/) with a link to download your .argosmodel file and some sample text that your model has translated.
* Pick an [issue](https://github.com/LibreTranslate/LibreTranslate/issues) to work on.

## Credits

This work is largely possible thanks to [Argos Translate](https://github.com/argosopentech/argos-translate), which powers the translation engine.

## License

[GNU Affero General Public License v3](https://www.gnu.org/licenses/agpl-3.0.en.html)

## Trademark

See [Trademark Guidelines](https://github.com/LibreTranslate/LibreTranslate/blob/main/TRADEMARK.md)
