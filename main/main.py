import time

from object import Config, PrayerTime, Location, logger


def start_prayer_notification():
    # initialize object
    conf = Config()
    conf.get_config()

    loc = Location(conf.location)

    pt = PrayerTime()
    # get & set prayer time
    prayer_time = pt.get_prayer_time(loc)
    pt.set_prayer_time(prayer_time)

    # start notif
    logger.info('Prayer time set. App is running')
    while True:
        try:
            pt.start_notify(reminder_time=conf.reminder_time)
            time.sleep(1)
        except Exception as e:
            if isinstance(e, StopIteration):
                return start_prayer_notification()
            else:
                logger.error(str(e))
                return

if __name__ == '__main__':
    logger.info('App initiating')
    start_prayer_notification()

    




