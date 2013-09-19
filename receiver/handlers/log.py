from lamson.routing import route, stateless 
import logging, os
import spampot

def log_handler():
  @route("(to)@(host)", to=".+", host=".+")
  @stateless
  def START(message, to=None, host=None):
    #logging.debug("MESSAGE to %s@%s:\n%s" % (to, host, str(message)))
    logging.debug("MESSAGE to %s@%s" % (to, host))
