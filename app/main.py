import argparse
import sys
import operator

from app.app import create_app
from app.default_values import DEFAULT_ARGUMENTS as DEFARGS


def main():
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
        help="Set the maximum number of request limit offences per 4 weeks that a client can exceed before being banned. (%(default)s)",
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
        "--require-api-key-origin",
        type=str,
        default=DEFARGS['REQUIRE_API_KEY_ORIGIN'],
        help="Require use of an API key for programmatic access to the API, unless the request origin matches this domain",
    )
    parser.add_argument(
        "--load-only",
        type=operator.methodcaller("split", ","),
        default=DEFARGS['LOAD_ONLY'],
        metavar="<comma-separated language codes>",
        help="Set available languages (ar,de,en,es,fr,ga,hi,it,ja,ko,pt,ru,zh)",
    )
    parser.add_argument(
        "--suggestions", default=DEFARGS['SUGGESTIONS'], action="store_true", help="Allow user suggestions"
    )

    args = parser.parse_args()
    app = create_app(args)

    if sys.argv[0] == '--wsgi':
        return app
    else:
        if args.debug:
            app.run(host=args.host, port=args.port)
        else:
            from waitress import serve

            serve(
                app,
                host=args.host,
                port=args.port,
                url_scheme="https" if args.ssl else "http",
            )


if __name__ == "__main__":
    main()
