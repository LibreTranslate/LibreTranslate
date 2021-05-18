import argparse

from app.api_keys import Database


def manage():
    parser = argparse.ArgumentParser(description="LibreTranslate Manage Tools")
    subparsers = parser.add_subparsers(
        help="", dest="command", required=True, title="Command List"
    )

    keys_parser = subparsers.add_parser("keys", help="Manage API keys database")
    keys_subparser = keys_parser.add_subparsers(
        help="", dest="sub_command", title="Command List"
    )

    keys_add_parser = keys_subparser.add_parser("add", help="Add API keys to database")
    keys_add_parser.add_argument(
        "req_limit", type=int, help="Request Limits (per second)"
    )
    keys_add_parser.add_argument(
        "--key", type=str, default="auto", required=False, help="API Key"
    )

    keys_remove_parser = keys_subparser.add_parser(
        "remove", help="Remove API keys to database"
    )
    keys_remove_parser.add_argument("key", type=str, help="API Key")

    args = parser.parse_args()

    if args.command == "keys":
        db = Database()
        if args.sub_command is None:
            # Print keys
            keys = db.all()
            if not keys:
                print("There are no API keys")
            else:
                for item in keys:
                    print("%s: %s" % item)

        elif args.sub_command == "add":
            print(db.add(args.req_limit, args.key)[0])
        elif args.sub_command == "remove":
            print(db.remove(args.key))
    else:
        parser.print_help()
        exit(1)
