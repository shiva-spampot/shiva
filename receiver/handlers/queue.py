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
import re
import spampot

def queue_handler():
  @route("(to)@(host)", to=".+", host=".+")
  @stateless
  @nolocking
  def START(message, to=None, host=None):
    q = queue.Queue(spampot.pathOfQueue)
    '''
    lamson has been found missing delivering mails to recipients in 'cc' and 'bcc'.
    Upto this point, lamson perfectly determines recipients combining 'to' and 'host' variables but always pushes 'message' in queue.
    The issue is, 'message' contains just the original 'To' recipent. Hence, though lamson successfully determines 'cc'/'bcc', the 'message' misses that.
    Using following dirty regex, 'To' field is replaced with next 'cc'/'bcc' recipient with each iteration.
    If, including 'To', there are 4 recipient in 'cc'/'bcc', total 5 mails would be pushed in queue.
    
    '''
    email = "%s@%s" % (to, host)
    message = str(message).replace("%", "%%")
    new_msg = re.sub(r'(?m)^\To:.*\n?', 'To: %s\n', message, 1) % (email,)
    q.push(new_msg) 