import atexit
import random
import string
from multiprocessing import Value

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

def secret_match(secret):
    s = get_storage()
    return secret == s.get_str("secret_0") or secret == s.get_str("secret_1")

def get_current_secret():
    return get_storage().get_str("secret_1")

def setup():
    # Only setup the scheduler and secrets on one process
    if not setup_secrets.value:
        setup_secrets.value = True
        
        s = get_storage()
        s.set_str("secret_0", generate_secret())
        s.set_str("secret_1", generate_secret())
        
        scheduler = BackgroundScheduler()
        scheduler.add_job(func=rotate_secrets, trigger="interval", minutes=30)
        
        scheduler.start()

        # Shut down the scheduler when exiting the app
        atexit.register(lambda: scheduler.shutdown())
