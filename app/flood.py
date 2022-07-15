import atexit

from apscheduler.schedulers.background import BackgroundScheduler

banned = {}
active = False
threshold = -1


def forgive_banned():
    global banned
    global threshold

    clear_list = []

    for ip in banned:
        if banned[ip] <= 0:
            clear_list.append(ip)
        else:
            banned[ip] = min(threshold, banned[ip]) - 1

    for ip in clear_list:
        del banned[ip]


def setup(violations_threshold=100):
    global active
    global threshold

    active = True
    threshold = violations_threshold

    scheduler = BackgroundScheduler()
    scheduler.add_job(func=forgive_banned, trigger="interval", minutes=30)
    scheduler.start()

    # Shut down the scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown())


def report(request_ip):
    if active:
        banned[request_ip] = banned.get(request_ip, 0)
        banned[request_ip] += 1


def decrease(request_ip):
    if banned[request_ip] > 0:
        banned[request_ip] -= 1


def has_violation(request_ip):
    return request_ip in banned and banned[request_ip] > 0


def is_banned(request_ip):
    # More than X offences?
    return active and banned.get(request_ip, 0) >= threshold
