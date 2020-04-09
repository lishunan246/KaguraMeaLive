import atexit

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from KaguraMeaLive import app


def init_background_jobs():
    scheduler = BackgroundScheduler()
    from .subscribe import subscribe_job
    scheduler.add_job(subscribe_job, CronTrigger.from_crontab('0 0 * * *'))
    from .twitcasting import scan_twitcasting
    scheduler.add_job(scan_twitcasting, 'interval', seconds=30)
    scheduler.start()

    # Shut down the scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown())
    app.logger.info("background tasks inited.")
