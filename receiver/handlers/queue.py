""" 
 2  Implements a handler that puts every message it receives into  
 3  the run/queue directory.  It is intended as a debug tool so you 
 4  can inspect messages the server is receiving using mutt or  
 5  the lamson queue command. 
 6  """ 
 
from lamson.routing import route_like, stateless, nolocking, route
from lamson import queue, handlers 
import logging
import os, time
from config import settings	# for forward handler
import shutil
import spampot

def queue_handler():
  @route("(to)@(host)", to=".+", host=".+")
  @stateless
  @nolocking
  def START(message, to=None, host=None):
    q = queue.Queue(spampot.pathOfQueue)
    q.push(message) 