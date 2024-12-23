import os
import config


def init_receiver():
    """
    This function is supposed to run before server start for setting up/confirming various
    required things.
    :return:
    """
    # Creating queue and other directories if they don't exist.
    os.makedirs(config.QUEUE_DIR, exist_ok=True)
