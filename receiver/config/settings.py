# This file contains python variables that configure Lamson for email processing.
import logging
import ConfigParser
import os

confpath = os.path.dirname(os.path.realpath(__file__)) + "/../../../shiva.conf"
config = ConfigParser.ConfigParser()
config.read(confpath)
host = config.get('receiver', 'listenhost')
port = config.getint('receiver', 'listenport')

relay_config = {'host': 'localhost', 'port': 8825}
receiver_config = {'host': host, 'port': port}
handlers = ['app.handlers.spampot']
router_defaults = {'host': '.+'}
template_config = {'dir': 'app', 'module': 'templates'}