import atexit

from apscheduler.schedulers.background import BackgroundScheduler

scheduler = None

def setup(args):
    from libretranslate.flood import forgive_banned
    from libretranslate.secret import rotate_secrets

    global scheduler

    if scheduler is None:
        scheduler = BackgroundScheduler()

        if args.req_flood_threshold > 0:
            scheduler.add_job(func=forgive_banned, trigger="interval", minutes=10)

        if args.api_keys and args.require_api_key_secret:
            scheduler.add_job(func=rotate_secrets, trigger="interval", minutes=30)

        scheduler.start()

        # Shut down the scheduler when exiting the app
        atexit.register(lambda: scheduler.shutdown())