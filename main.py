import argparse
from app.app import create_app

parser = argparse.ArgumentParser(description='LibreTranslate - Free and Open Source Translation API')
parser.add_argument('--host', type=str,
                    help='Hostname (%(default)s)', default="127.0.0.1")
parser.add_argument('--port', type=int,
                    help='Port (%(default)s)', default=5000)
parser.add_argument('--char-limit', default=-1, metavar="<number of characters>",
                    help='Set character limit (%(default)s)')
parser.add_argument('--req-limit', default=-1, type=int, metavar="<number>",
                    help='Set maximum number of requests per minute per client (%(default)s)')
parser.add_argument('--google-analytics', type=str, default=None, metavar="<GA ID>",
                    help='Enable Google Analytics on the API client page by providing an ID (%(default)s)')
parser.add_argument('--debug', default=False, action="store_true",
                    help="Enable debug environment")
parser.add_argument('--ssl', default=None, action="store_true",
                    help="Whether to enable SSL")

args = parser.parse_args()


if __name__ == "__main__":
    app = create_app(char_limit=args.char_limit, 
                     req_limit=args.req_limit,
                     google_analytics=args.google_analytics,
                     debug=args.debug)
    if args.debug:
        app.run(host=args.host, port=args.port)
    else:
        from waitress import serve
        serve(app, host=args.host, port=args.port, url_scheme='https' if args.ssl else 'http')