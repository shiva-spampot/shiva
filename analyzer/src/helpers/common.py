import datetime


def get_utc_datetime():
    return datetime.datetime.now(datetime.timezone.utc)
