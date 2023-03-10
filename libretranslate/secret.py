import atexit
import random
import string
from multiprocessing.dummy import Value

from libretranslate.storage import get_storage
from apscheduler.schedulers.background import BackgroundScheduler

setup_secrets = Value('b', False)

def generate_secret():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=7))

def rotate_secrets():
    s = get_storage()
    secret_1 = s.get_str("secret_1")
    s.set_str("secret_0", secret_1)
    s.set_str("secret_1", generate_secret())
    print(s.get_str("secret_0"))
    print(s.get_str("secret_1"))
    

def secret_match(secret):
    s = get_storage()
    return secret == s.get_str("secret_0") or secret == s.get_str("secret_1")

def get_current_secret():
    return get_storage().get_str("secret_1")

def setup(args):
    if args.api_keys and args.require_api_key_secret:
        s = get_storage()
        s.set_str("secret_0", generate_secret())
        s.set_str("secret_1", generate_secret())
