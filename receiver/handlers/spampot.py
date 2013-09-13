# Customised handler
# Atm, only handler that gets called and is loaded in settings.py modules
# It further loads the handlers - log and queue
# queue handler further takes care of calling "forward" handler

import log, queue, forward	# Our modules in app/handlers
import logging, os
import ConfigParser

confpath = os.path.dirname(os.path.realpath(__file__)) + "/../../../../shiva.conf"
config = ConfigParser.ConfigParser()
config.read(confpath)
host = config.get('receiver', 'listenhost')

pathOfQueue = config.get('global', 'queuepath')	# Path of queue where new message arrives
pathOfUndelivered = 'run/undeliverable/new/'	# Path for undelivered mails
pathOfArchive = 'logs/archive/'	 # Archive path for all spams received, push them to DB later

log.log_handler()
queue.queue_handler()