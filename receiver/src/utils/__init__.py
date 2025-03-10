import logging
import logging.handlers
import os
import pathlib
from config import config
import warnings

warnings.filterwarnings("ignore", category=UserWarning, message="Requiring AUTH while not requiring TLS can lead to security vulnerabilities!")

def get_logger():
    log_level = config["logging"]["level"]
    log_type = config["logging"]["type"]
    log_filename = config["logging"]["filename"]
    max_bytes = int(config["logging"]["max_bytes"])
    backup_count = int(config["logging"]["backup_count"])
    format = config["logging"]["format"]
    folder_path = config["logging"]["folder_path"]

    # Set up logging level
    level = getattr(logging, log_level.upper(), logging.DEBUG)

    project_root = get_parent_folder()
    logging_folder = os.path.join(project_root, folder_path)
    log_path = os.path.join(logging_folder, log_filename)
    os.makedirs(logging_folder, exist_ok=True)

    # Configure logging based on the type
    if log_type == "console":
        handler = logging.StreamHandler()
    elif log_type == "file":
        handler = logging.handlers.RotatingFileHandler(
            log_path, maxBytes=max_bytes, backupCount=backup_count
        )
    else:
        raise ValueError(f"Unknown log type: {log_type}")

    # Set up the logger
    logging.basicConfig(
        level=level,
        handlers=[handler],
        format=format,
    )

    return logging.getLogger()


def get_parent_folder():
    return pathlib.Path(os.path.dirname(os.path.abspath(__file__))).parent
