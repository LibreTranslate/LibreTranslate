import argparse
import operator
import sys

from libretranslate.app import create_app
from libretranslate.default_values import DEFAULT_ARGUMENTS as DEFARGS


def get_args():
    parser = argparse.ArgumentParser(
        description="LibreTranslate - Free and Open Source Translation API"
    )
    parser.add_argument(
        "--host", type=str, help="Hostname (%(default)s)", default=DEFARGS['HOST']
    )
    parser.add_argument("--port", type=int, help="Port (%(default)s)", default=DEFARGS['PORT'])
    parser.add_argument(
        "--char-limit",
        default=DEFARGS['CHAR_LIMIT'],
        type=int,
        metavar="<number of characters>",
        help="Set character limit (%(default)s)",
    )
    parser.add_argument(
        "--req-limit",
        default=DEFARGS['REQ_LIMIT'],
        type=int,
        metavar="<number>",
        help="Set the default maximum number of requests per minute per client (%(default)s)",
    )
    parser.add_argument(
        "--req-limit-storage",
        default=DEFARGS['REQ_LIMIT_STORAGE'],
        type=str,
        metavar="<Storage URI>",
        help="Storage URI to use for request limit data storage. See https://flask-limiter.readthedocs.io/en/stable/configuration.html. (%(default)s)",
    )
    parser.add_argument(
        "--hourly-req-limit",
        default=DEFARGS['HOURLY_REQ_LIMIT'],
        type=int,
        metavar="<number>",
        help="Set the default maximum number of requests per hour per client, in addition to req-limit. (%(default)s)",
    )
    parser.add_argument(
        "--hourly-req-limit-decay",
        default=DEFARGS['HOURLY_REQ_LIMIT_DECAY'],
        type=int,
        metavar="<number>",
        help="When used in combination with hourly-req-limit, adds additional hourly restrictions that logaritmically decrease for each additional hour. (%(default)s)",
    )
    parser.add_argument(
        "--daily-req-limit",
        default=DEFARGS['DAILY_REQ_LIMIT'],
        type=int,
        metavar="<number>",
        help="Set the default maximum number of requests per day per client, in addition to req-limit. (%(default)s)",
    )
    parser.add_argument(
        "--req-flood-threshold",
        default=DEFARGS['REQ_FLOOD_THRESHOLD'],
        type=int,
        metavar="<number>",
        help="Set the maximum number of request limit offences that a client can exceed before being banned. (%(default)s)",
    )
    parser.add_argument(
        "--req-time-cost",
        default=DEFARGS['REQ_TIME_COST'],
        type=int,
        metavar="<number>",
        help="Considers a time cost (in seconds) for request limiting purposes. If a request takes 10 seconds and this value is set to 5, the request cost is either 2 or the actual request cost (whichever is greater). (%(default)s)",
    )
    parser.add_argument(
        "--batch-limit",
        default=DEFARGS['BATCH_LIMIT'],
        type=int,
        metavar="<number of texts>",
        help="Set maximum number of texts to translate in a batch request (%(default)s)",
    )
    parser.add_argument(
        "--ga-id",
        type=str,
        default=DEFARGS['GA_ID'],
        metavar="<GA ID>",
        help="Enable Google Analytics on the API client page by providing an ID (%(default)s)",
    )
    parser.add_argument(
        "--debug", default=DEFARGS['DEBUG'], action="store_true", help="Enable debug environment"
    )
    parser.add_argument(
        "--ssl", default=DEFARGS['SSL'], action="store_true", help="Whether to enable SSL"
    )
    parser.add_argument(
        "--frontend-language-source",
        type=str,
        default=DEFARGS['FRONTEND_LANGUAGE_SOURCE'],
        metavar="<language code>",
        help="Set frontend default language - source (%(default)s)",
    )
    parser.add_argument(
        "--frontend-language-target",
        type=str,
        default=DEFARGS['FRONTEND_LANGUAGE_TARGET'],
        metavar="<language code>",
        help="Set frontend default language - target (%(default)s)",
    )
    parser.add_argument(
        "--frontend-timeout",
        type=int,
        default=DEFARGS['FRONTEND_TIMEOUT'],
        metavar="<milliseconds>",
        help="Set frontend translation timeout (%(default)s)",
    )
    parser.add_argument(
        "--api-keys",
        default=DEFARGS['API_KEYS'],
        action="store_true",
        help="Enable API keys database for per-user rate limits lookup",
    )
    parser.add_argument(
        "--api-keys-db-path",
        default=DEFARGS['API_KEYS_DB_PATH'],
        type=str,
        help="Use a specific path inside the container for the local database. Can be absolute or relative (%(default)s)",
    )
    parser.add_argument(
        "--api-keys-remote",
        default=DEFARGS['API_KEYS_REMOTE'],
        type=str,
        help="Use this remote endpoint to query for valid API keys instead of using the local database",
    )
    parser.add_argument(
        "--get-api-key-link",
        default=DEFARGS['GET_API_KEY_LINK'],
        type=str,
        help="Show a link in the UI where to direct users to get an API key",
    )
    parser.add_argument(
        "--require-api-key-origin",
        type=str,
        default=DEFARGS['REQUIRE_API_KEY_ORIGIN'],
        help="Require use of an API key for programmatic access to the API, unless the request origin matches this domain",
    )
    parser.add_argument(
        "--require-api-key-secret",
        default=DEFARGS['REQUIRE_API_KEY_SECRET'],
        action="store_true",
        help="Require use of an API key for programmatic access to the API, unless the client also sends a secret match",
    )
    parser.add_argument(
        "--shared-storage",
        type=str,
        default=DEFARGS['SHARED_STORAGE'],
        metavar="<Storage URI>",
        help="Shared storage URI to use for multi-process data sharing (e.g. via gunicorn)",
    )
    parser.add_argument(
        "--load-only",
        type=operator.methodcaller("split", ","),
        default=DEFARGS['LOAD_ONLY'],
        metavar="<comma-separated language codes>",
        help="Set available languages (ar,de,en,es,fr,ga,hi,it,ja,ko,pt,ru,zh)",
    )
    parser.add_argument(
        "--threads",
        default=DEFARGS['THREADS'],
        type=int,
        metavar="<number of threads>",
        help="Set number of threads (%(default)s)",
    )
    parser.add_argument(
        "--suggestions", default=DEFARGS['SUGGESTIONS'], action="store_true", help="Allow user suggestions"
    )
    parser.add_argument(
        "--disable-files-translation", default=DEFARGS['DISABLE_FILES_TRANSLATION'], action="store_true",
        help="Disable files translation"
    )
    parser.add_argument(
        "--disable-web-ui", default=DEFARGS['DISABLE_WEB_UI'], action="store_true", help="Disable web ui"
    )
    parser.add_argument(
        "--update-models", default=DEFARGS['UPDATE_MODELS'], action="store_true", help="Update language models at startup"
    )
    parser.add_argument(
        "--force-update-models", default=DEFARGS['FORCE_UPDATE_MODELS'], action="store_true", help="Install/Reinstall language models at startup"
    )
    parser.add_argument(
        "--metrics",
        default=DEFARGS['METRICS'],
        action="store_true",
        help="Enable the /metrics endpoint for exporting Prometheus usage metrics",
    )
    parser.add_argument(
        "--metrics-auth-token",
        default=DEFARGS['METRICS_AUTH_TOKEN'],
        type=str,
        help="Protect the /metrics endpoint by allowing only clients that have a valid Authorization Bearer token (%(default)s)",
    )
    parser.add_argument(
        "--url-prefix",
        default=DEFARGS['URL_PREFIX'],
        type=str,
        help="Add prefix to URL: example.com:5000/url-prefix/",
    )
    args = parser.parse_args()
    if args.url_prefix and not args.url_prefix.startswith('/'):
        args.url_prefix = '/' + args.url_prefix
    return args


def main():
    args = get_args()
    app = create_app(args)

    if '--wsgi' in sys.argv:
        return app
    else:
        if args.debug:
            app.run(host=args.host, port=args.port)
        else:
            from waitress import serve

            url_scheme = "https" if args.ssl else "http"
            print(f"Running on {url_scheme}://{args.host}:{args.port}{args.url_prefix}")

            serve(
                app,
                host=args.host,
                port=args.port,
                url_scheme=url_scheme,
                threads=args.threads
            )


if __name__ == "__main__":
    main()
