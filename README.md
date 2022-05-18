# LibreTranslate

[Try it online!](https://libretranslate.com) | [API Docs](https://libretranslate.com/docs) | [Community Forum](https://community.libretranslate.com/)

[![Python versions](https://img.shields.io/pypi/pyversions/libretranslate)](https://pypi.org/project/libretranslate) [![Run tests](https://github.com/LibreTranslate/LibreTranslate/workflows/Run%20tests/badge.svg)](https://github.com/LibreTranslate/LibreTranslate/actions?query=workflow%3A%22Run+tests%22) [![Build and Publish Docker Image](https://github.com/LibreTranslate/LibreTranslate/actions/workflows/publish-docker.yml/badge.svg)](https://github.com/LibreTranslate/LibreTranslate/actions/workflows/publish-docker.yml) [![Publish package](https://github.com/LibreTranslate/LibreTranslate/actions/workflows/publish-package.yml/badge.svg)](https://github.com/LibreTranslate/LibreTranslate/actions/workflows/publish-package.yml) [![Awesome Humane Tech](https://raw.githubusercontent.com/humanetech-community/awesome-humane-tech/main/humane-tech-badge.svg?sanitize=true)](https://github.com/humanetech-community/awesome-humane-tech)

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

Then open a web browser to http://localhost:5000

If you're on Windows, we recommend you [Run with Docker](#run-with-docker) instead.

On Ubuntu 20.04 you can also use the install script available at https://github.com/argosopentech/LibreTranslate-init

If you would rather run it natively, you can follow the guide [here](https://github.com/nuttolum/LibreOnWindows).

## Build and Run

If you want to make changes to the code, you can build from source, and run the API:

```bash
git clone https://github.com/LibreTranslate/LibreTranslate
cd LibreTranslate
pip install -e .
libretranslate [args]

# Or
python main.py [args]
```

Then open a web browser to http://localhost:5000

### Run with Docker

Simply run:

```bash
docker run -ti --rm -p 5000:5000 libretranslate/libretranslate
```

Then open a web browser to http://localhost:5000

### Build with Docker

```bash
docker build [--build-arg with_models=true] -t libretranslate .
```

If you want to run the Docker image in a complete offline environment, you need to add the `--build-arg with_models=true` parameter. Then the language models are downloaded during the build process of the image. Otherwise these models get downloaded on the first run of the image/container.

Run the built image:

```bash
docker run -it -p 5000:5000 libretranslate [args]
```

Or build and run using `docker-compose`:

```bash
docker-compose up -d --build
```

> Feel free to change the [`docker-compose.yml`](https://github.com/LibreTranslate/LibreTranslate/blob/main/docker-compose.yml) file to adapt it to your deployment needs, or use an extra `docker-compose.prod.yml` file for your deployment configuration.

## Arguments

| Argument                    | Description                                                                                                 | Default              | Env. name                    |
|-----------------------------|-------------------------------------------------------------------------------------------------------------| -------------------- |------------------------------|
| --host                      | Set host to bind the server to                                                                              | `127.0.0.1`          | LT_HOST                      |
| --port                      | Set port to bind the server to                                                                              | `5000`               | LT_PORT                      |
| --char-limit                | Set character limit                                                                                         | `No limit`               | LT_CHAR_LIMIT                |
| --req-limit                 | Set maximum number of requests per minute per client                                                        | `No limit`               | LT_REQ_LIMIT                 |
| --batch-limit               | Set maximum number of texts to translate in a batch request                                                 | `No limit`               | LT_BATCH_LIMIT               |
| --ga-id                     | Enable Google Analytics on the API client page by providing an ID                                           | `No tracking`               | LT_GA_ID                     |
| --debug                     | Enable debug environment                                                                                    | `False`           | LT_DEBUG                     |
| --ssl                       | Whether to enable SSL                                                                                       | `False`               | LT_SSL                       |
| --frontend-language-source  | Set frontend default language - source                                                                      | `en`          | LT_FRONTEND_LANGUAGE_SOURCE  |
| --frontend-language-target  | Set frontend default language - target                                                                      | `es`          | LT_FRONTEND_LANGUAGE_TARGET  |
| --frontend-timeout          | Set frontend translation timeout                                                                            | `500`         | LT_FRONTEND_TIMEOUT          |
| --api-keys                  | Enable API keys database for per-user rate limits lookup                                                    | `Don't use API keys` | LT_API_KEYS                  |
| --require-api-key-origin    | Require use of an API key for programmatic access to the API, unless the request origin matches this domain | `No restrictions on domain origin` | LT_REQUIRE_API_KEY_ORIGIN    |
| --load-only                 | Set available languages                                                                                     | `all from argostranslate`    | LT_LOAD_ONLY                 |
| --suggestions               | Allow user suggestions                                                                                      | `false`    | LT_SUGGESTIONS               |
| --disable-files-translation | Disable files translation                                                                                   | `false`    | LT_DISABLE_FILES_TRANSLATION |
| --disable-web-ui            | Disable web ui                                                                                              | `false`    | LT_DISABLE_WEB_UI            |

Note that each argument has an equivalent environment variable that can be used instead. The env. variables overwrite the default values but have lower priority than the command aguments and are particularly useful if used with Docker. The environment variable names are the upper-snake-case of the equivalent command argument's name with a `LT` prefix.

## Run with WSGI and Gunicorn

```
pip install gunicorn
gunicorn --bind 0.0.0.0:5000 'wsgi:app'
```

You can pass application arguments directly to Gunicorn via:


```
gunicorn --bind 0.0.0.0:5000 'wsgi:app(api_keys=True)'
```

## Run with Kubernetes

See ["LibreTranslate: your own translation service on Kubernetes" by JM Robles](https://jmrobles.medium.com/libretranslate-your-own-translation-service-on-kubernetes-b46c3e1af630)

## Manage API Keys

LibreTranslate supports per-user limit quotas, e.g. you can issue API keys to users so that they can enjoy higher requests limits per minute (if you also set `--req-limit`). By default all users are rate-limited based on `--req-limit`, but passing an optional `api_key` parameter to the REST endpoints allows a user to enjoy higher request limits.

To use API keys simply start LibreTranslate with the `--api-keys` option.

### Add New Keys

To issue a new API key with 120 requests per minute limits:

```bash
ltmanage keys add 120
```

### Remove Keys

```bash
ltmanage keys remove <api-key>
```

### View Keys

```bash
ltmanage keys
```

## Language Bindings

You can use the LibreTranslate API using the following bindings:

 - Rust: https://github.com/DefunctLizard/libretranslate-rs
 - Node.js: https://github.com/franciscop/translate
 - .Net: https://github.com/sigaloid/LibreTranslate.Net
 - Go: https://github.com/SnakeSel/libretranslate
 - Python: https://github.com/argosopentech/LibreTranslate-py
 - PHP: https://github.com/jefs42/libretranslate
 - C++: https://github.com/argosopentech/LibreTranslate-cpp
 - Unix: https://github.com/argosopentech/LibreTranslate-sh

## Discourse Plugin

You can use this [discourse translator plugin](https://github.com/LibreTranslate/discourse-translator) to translate [Discourse](https://discourse.org) topics. To install it simply modify `/var/discourse/containers/app.yml`:

```
## Plugins go here
## see https://meta.discourse.org/t/19157 for details
hooks:
  after_code:
    - exec:
        cd: $home/plugins
        cmd:
          - git clone https://github.com/discourse/docker_manager.git
          - git clone https://github.com/LibreTranslate/discourse-translator
	  ...
```

Then issue `./launcher rebuild app`. From the Discourse's admin panel then select "LibreTranslate" as a translation provider and set the relevant endpoint configurations.

## Mobile Apps

- [LibreTranslater](https://gitlab.com/BeowuIf/libretranslater) is an Android app [available on the Play Store](https://play.google.com/store/apps/details?id=de.beowulf.libretranslater) and [in the F-Droid store](https://f-droid.org/packages/de.beowulf.libretranslater/) that uses the LibreTranslate API.

## Web browser
- [minbrowser](https://minbrowser.org/) is a web browser with [integrated LibreTranslate support](https://github.com/argosopentech/argos-translate/discussions/158#discussioncomment-1141551).
- A LibreTranslate Firefox addon is [currently a work in progress](https://github.com/LibreTranslate/LibreTranslate/issues/55).

## Mirrors

This is a list of public LibreTranslate instances, some require an API key. If you want to add a new URL, please open a pull request.

URL |API Key Required|Payment Link|Cost
--- | --- | --- | ---
[libretranslate.com](https://libretranslate.com)|:heavy_check_mark:|[Buy](https://buy.stripe.com/3cs4j3a4u4c8d3i289)| [$19 / month](https://buy.stripe.com/3cs4j3a4u4c8d3i289), 80 requests / minute limit
[libretranslate.de](https://libretranslate.de)|-|-
[translate.argosopentech.com](https://translate.argosopentech.com/)|-|-
[translate.api.skitzen.com](https://translate.api.skitzen.com/)|-|-
[libretranslate.pussthecat.org](https://libretranslate.pussthecat.org/)|-|-
[translate.fortytwo-it.com](https://translate.fortytwo-it.com/)|-|-
[translate.terraprint.co](https://translate.terraprint.co/)|-|-

## Adding New Languages

To add new languages you first need to train an Argos Translate model. See [this video](https://odysee.com/@argosopentech:7/training-an-Argos-Translate-model-tutorial-2022:2?r=DMnK7NqdPNHRCfwhmKY9LPow3PqVUUgw) for details.

First you need to collect data, for example from [Opus](http://opus.nlpl.eu/), then you need to add the data to [data-index.json](https://github.com/argosopentech/argos-train/blob/master/data-index.json) in the [Argos Train](https://github.com/argosopentech/argos-train) repo.

## Roadmap

Help us by opening a pull request!

- [x] A docker image (thanks [@vemonet](https://github.com/vemonet) !)
- [x] Auto-detect input language (thanks [@vemonet](https://github.com/vemonet) !)
- [X] User authentication / tokens
- [ ] Language bindings for every computer language
- [ ] [Improved translations](https://community.libretranslate.com/t/the-best-way-to-train-models/172)

## FAQ

### Can I use your API server at libretranslate.com for my application in production?

In short, no. [You need to buy an API key](https://buy.stripe.com/3cs4j3a4u4c8d3i289). You can always run LibreTranslate for free on your own server of course.

### Can I use LibreTranslate behind a reverse proxy, like Apache2?

Yes, here is an example Apache2 config that redirects a subdomain (with HTTPS certificate) to LibreTranslate running on a docker at localhost. 
```
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

## Credits

This work is largely possible thanks to [Argos Translate](https://github.com/argosopentech/argos-translate), which powers the translation engine.

## License

[GNU Affero General Public License v3](https://www.gnu.org/licenses/agpl-3.0.en.html)

## Trademark

See [Trademark Guidelines](https://github.com/LibreTranslate/LibreTranslate/blob/main/TRADEMARK.md)
