import random
import string

from libretranslate.storage import get_storage


def generate_secret():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=7))

def rotate_secrets():
    s = get_storage()
    secret_1 = s.get_str("secret_1")
    s.set_str("secret_0", secret_1)
    s.set_str("secret_1", generate_secret())


def secret_match(secret):
    s = get_storage()
    return secret == s.get_str("secret_0") or secret == s.get_str("secret_1")

def get_current_secret():
    return get_storage().get_str("secret_1")

def setup(args):
    if args.api_keys and args.require_api_key_secret:
        s = get_storage()

        if not s.exists("secret_0"):
            s.set_str("secret_0", generate_secret())

        if not s.exists("secret_1"):
            s.set_str("secret_1", generate_secret())
