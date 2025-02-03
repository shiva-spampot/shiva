import configparser
import os


def get_config():
    config_obj = configparser.ConfigParser(interpolation=None)
    config_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "config.ini",
    )
    config_obj.read(config_path)
    return config_obj


config = get_config()
