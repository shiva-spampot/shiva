import os
from socket import getfqdn

SHIVA_HOST = os.environ.get("SHIVA_HOST", "127.0.0.1")
SHIVA_PORT = int(os.environ.get("SHIVA_PORT", 2525))
QUEUE_DIR = os.environ.get("QUEUE_DIR", "/tmp/spam_queue/")
SENSOR_NAME = os.environ.get("SENSOR_NAME", getfqdn())
