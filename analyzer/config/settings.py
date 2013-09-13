# This file contains python variables that configure Lamson for email processing.
import logging
import ConfigParser
import os


confpath = os.path.dirname(os.path.realpath(__file__)) + "/../../../shiva.conf"
config = ConfigParser.ConfigParser()
config.read(confpath)

queuePath = config.get('global', 'queuepath')
relayhost = config.get('analyzer', 'relayhost')
relayport = config.getint('analyzer', 'relayport')

relay_config = {'host': relayhost, 'port': relayport}
receiver_config = {'maildir': queuePath}
handlers = ['app.handlers.sample']
router_defaults = {'host': '.+'}
template_config = {'dir': 'app', 'module': 'templates'}