from config import settings
from lamson.routing import Router
from lamson.server import Relay, SMTPReceiver, QueueReceiver
from lamson import view, queue
import logging
import logging.config
import jinja2

logging.config.fileConfig("config/logging.conf")

# Relay host to actually send the final message to.
settings.relay = Relay(host=settings.relay_config['host'], 
                       port=settings.relay_config['port'], debug=0)

# Include the maildir option we've set in settings.py
settings.receiver = QueueReceiver(settings.receiver_config['maildir'])

Router.defaults(**settings.router_defaults)
Router.load(settings.handlers)
Router.RELOAD=True
Router.UNDELIVERABLE_QUEUE=queue.Queue("run/undeliverable")

view.LOADER = jinja2.Environment(
    loader=jinja2.PackageLoader(settings.template_config['dir'], 
                                settings.template_config['module']))

