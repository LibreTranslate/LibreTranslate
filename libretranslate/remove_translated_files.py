import atexit
import os
import time
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler


def remove_translated_files(upload_dir: str):
    now = time.mktime(datetime.now().timetuple())

    for f in os.listdir(upload_dir):
        f = os.path.join(upload_dir, f)
        if os.path.isfile(f):
            f_time = os.path.getmtime(f)
            if (now - f_time) > 1800:  # 30 minutes
                os.remove(f)


def setup(upload_dir):
    scheduler = BackgroundScheduler(daemon=True)
    scheduler.add_job(remove_translated_files, "interval", minutes=30, kwargs={'upload_dir': upload_dir})
    scheduler.start()

    # Shut down the scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown())
