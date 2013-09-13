 
""" 
 2  Implements a forwarding handler that will take anything it receives and 
 3  forwards it to the relay host.  It is intended to use with the 
 4  lamson.routing.RoutingBase.UNDELIVERABLE_QUEUE if you want mail that Lamson 
 5  doesn't understand to be delivered like normal.  The Router will dump 
 6  any mail that doesn't match into that queue if you set it, and then you can 
 7  load this handler into a special queue receiver to have it forwarded on. 
 8   
 9  BE VERY CAREFUL WITH THIS.  It should only be used in testing scenarios as 
10  it can turn your server into an open relay if you're not careful.  You 
11  are probably better off writing your own version of this that knows a list 
12  of allowed hosts your machine answers to and only forwards those. 
13  """ 
  
from lamson.routing import route, stateless 
from config import settings 
import logging, os
import spampot

#os.system("echo 'forward-after-import' >> /root/Desktop/LamsonHoneyMail/MyMailServer/test.txt")

def forward_handler():
  @route("(to)@(host)", to=".+", host=".+")
  @stateless
  def START(message, to=None, host=None):
    logging.debug("MESSAGE to %s@%s forwarded to the relay host.", to, host)
    settings.relay.deliver(message)
    #test_fd = open("/root/Desktop/LamsonHoneyMail/MyMailServer/test.txt", 'a')
    debugFd = open(spampot.cwd + '/' + spampot.debugFile, 'a')
    debugFd.write("[+] >>>>>>> Executed handlers.FORWARD \n")
    debugFd.close()
