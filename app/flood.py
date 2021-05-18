import atexit

from apscheduler.schedulers.background import BackgroundScheduler

banned = {}
active = False
threshold = -1


def clear_banned():
    global banned
    banned = {}


def setup(violations_threshold=100):
    global active
    global threshold

    active = True
    threshold = violations_threshold

    scheduler = BackgroundScheduler()
    scheduler.add_job(func=clear_banned, trigger="interval", weeks=4)
    scheduler.start()

    # Shut down the scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown())


def report(request_ip):
    if active:
        banned[request_ip] = banned.get(request_ip, 0)
        banned[request_ip] += 1


def is_banned(request_ip):
    # More than X offences?
    return active and banned.get(request_ip, 0) >= threshold
