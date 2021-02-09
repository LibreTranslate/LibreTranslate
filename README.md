# LibreTranslate

[Try it online!](https://libretranslate.com) | [API Docs](https://libretranslate.com/docs)

[![Publish to DockerHub](https://github.com/uav4geo/LibreTranslate/workflows/Publish%20to%20DockerHub/badge.svg)](https://hub.docker.com/r/libretranslate/libretranslate) ![Publish to GitHub Container Registry](https://github.com/uav4geo/LibreTranslate/workflows/Publish%20to%20GitHub%20Container%20Registry/badge.svg)

Free and Open Source Machine Translation API, entirely self-hosted. Unlike other APIs, it doesn't rely on proprietary providers such as Google or Azure to perform translations.

![image](https://user-images.githubusercontent.com/1951843/102724116-32a6df00-42db-11eb-8cc0-129ab39cdfb5.png)

[Try it online!](https://libretranslate.com) | [API Docs](https://libretranslate.com/docs)

## API Examples

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

## Install and Run

You can run your own API server in just a few lines of setup!

Make sure you have installed Python (3.8 or higher), then simply issue:

```bash
pip install libretranslate
libretranslate [args]
```

Then open a web browser to http://localhost:5000

## Build and Run

If you want to make some changes to the code, you can build from source, and run the API:

```bash
git clone https://github.com/uav4geo/LibreTranslate
cd LibreTranslate
pip install -e .
libretranslate [args]
```

Then open a web browser to http://localhost:5000

### Run with Docker

Simply run:

```bash
docker run -ti --rm -p 5000:5000 libretranslate/libretranslate
```

Then open a web browser to http://localhost:5000

### Build with Docker

Make sure you cloned the `models` submodule before building the Docker image:

```bash
docker build -t libretranslate .
```

Run the built image:

```bash
docker run -it -p 5000:5000 libretranslate [args]
```

Or build and run using `docker-compose`:

```bash
docker-compose up -d --build
```

> Feel free to change the [`docker-compose.yml`](https://github.com/uav4geo/LibreTranslate/blob/main/docker-compose.yml) file to adapt it to your deployment needs, or use an extra `docker-compose.prod.yml` file for your deployment configuration.

## Arguments

| Argument      | Description                    | Default              |
| ------------- | ------------------------------ | -------------------- |
| --host        | Set host to bind the server to | `127.0.0.1`          |
| --port        | Set port to bind the server to | `5000`               |
| --char-limit        | Set character limit | `No limit`               |
| --req-limit        | Set maximum number of requests per minute per client | `No limit`               |
| --batch-limit        | Set maximum number of texts to translate in a batch request | `No limit`               |
| --ga-id        | Enable Google Analytics on the API client page by providing an ID | `No tracking`               |
| --debug      | Enable debug environment | `False`           |
| --ssl        | Whether to enable SSL | `False`               |
| --frontend-language-source | Set frontend default language - source | `en`          |
| --frontend-language-target | Set frontend default language - target | `es`          |
| --frontend-timeout | Set frontend translation timeout | `500`         |


## Roadmap

Help us by opening a pull request!

- [x] A docker image (thanks [@vemonet](https://github.com/vemonet) !)
- [x] Auto-detect input language (thanks [@vemonet](https://github.com/vemonet) !)
- [ ] User authentication / tokens
- [ ] Language bindings for every computer language

## FAQ

### Can I use your API server at libretranslate.com for my application in production?

The API on libretranslate.com should be used for testing, personal or infrequent use. If you're going to run an application in production, please [get in touch](https://uav4geo.com/contact) to discuss options.

## Credits

This work is largely possible thanks to [Argos Translate](https://github.com/argosopentech/argos-translate), which powers the translation engine.

## License

[GNU Affero General Public License v3](https://www.gnu.org/licenses/agpl-3.0.en.html)
