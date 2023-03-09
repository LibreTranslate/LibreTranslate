import atexit
from multiprocessing import Value

from libretranslate.storage import get_storage
from apscheduler.schedulers.background import BackgroundScheduler


setup_scheduler = Value('b', False)
active = False
threshold = -1

def forgive_banned():
    global threshold

    clear_list = []
    s = get_storage()
    banned = s.get_all_hash_int("banned")

    for ip in banned:
        if banned[ip] <= 0:
            clear_list.append(ip)
        else:
            banned[ip] = min(threshold, banned[ip]) - 1

    for ip in clear_list:
        s.del_hash("banned", ip)

def setup(violations_threshold=100):
    global active
    global threshold

    active = True
    threshold = violations_threshold

    # Only setup the scheduler and secrets on one process
    if not setup_scheduler.value:
        setup_scheduler.value = True

        scheduler = BackgroundScheduler()
        scheduler.add_job(func=forgive_banned, trigger="interval", minutes=30)
        
        scheduler.start()

        # Shut down the scheduler when exiting the app
        atexit.register(lambda: scheduler.shutdown())


def report(request_ip):
    if active:
        get_storage().inc_hash_int("banned", request_ip)

def decrease(request_ip):
    s = get_storage()
    if s.get_hash_int("banned", request_ip) > 0:
        s.dec_hash_int("banned", request_ip)

def has_violation(request_ip):
    s = get_storage()
    return s.get_hash_int("banned", request_ip) > 0

def is_banned(request_ip):
    s = get_storage()

    # More than X offences?
    return active and s.get_hash_int("banned", request_ip) >= threshold
