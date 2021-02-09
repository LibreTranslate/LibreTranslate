import argparse
from app.app import create_app

def main():
    parser = argparse.ArgumentParser(description='LibreTranslate - Free and Open Source Translation API')
    parser.add_argument('--host', type=str,
                        help='Hostname (%(default)s)', default="127.0.0.1")
    parser.add_argument('--port', type=int,
                        help='Port (%(default)s)', default=5000)
    parser.add_argument('--char-limit', default=-1, type=int, metavar="<number of characters>",
                        help='Set character limit (%(default)s)')
    parser.add_argument('--req-limit', default=-1, type=int, metavar="<number>",
                        help='Set maximum number of requests per minute per client (%(default)s)')
    parser.add_argument('--batch-limit', default=-1, type=int, metavar="<number of texts>",
                        help='Set maximum number of texts to translate in a batch request (%(default)s)')
    parser.add_argument('--ga-id', type=str, default=None, metavar="<GA ID>",
                        help='Enable Google Analytics on the API client page by providing an ID (%(default)s)')
    parser.add_argument('--debug', default=False, action="store_true",
                        help="Enable debug environment")
    parser.add_argument('--ssl', default=None, action="store_true",
                        help="Whether to enable SSL")
    parser.add_argument('--frontend-language-source', type=str, default="en", metavar="<language code>",
                        help='Set frontend default language - source (%(default)s)')
    parser.add_argument('--frontend-language-target', type=str, default="es", metavar="<language code>",
                        help='Set frontend default language - target (%(default)s)')
    parser.add_argument('--frontend-timeout', type=int, default=500, metavar="<milliseconds>",
                        help='Set frontend translation timeout (%(default)s)')

    args = parser.parse_args()

    app = create_app(char_limit=args.char_limit,
                     req_limit=args.req_limit,
                     batch_limit=args.batch_limit,
                     ga_id=args.ga_id,
                     debug=args.debug,
                     frontend_language_source=args.frontend_language_source,
                     frontend_language_target=args.frontend_language_target,
                     frontend_timeout=args.frontend_timeout)
    if args.debug:
        app.run(host=args.host, port=args.port)
    else:
        from waitress import serve
        serve(app, host=args.host, port=args.port, url_scheme='https' if args.ssl else 'http')

if __name__ == "__main__":
    main()
