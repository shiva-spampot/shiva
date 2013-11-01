#!/usr/bin/python
""" subscribe.py
Description - Subscribes to the hpfeeds channel, receives the data and dumps it into a local file.
Usage - python subscribe.py
"""

import sys
import os
import Queue
import threading
import cPickle
import datetime
 
import hpfeeds

WORKERS = 2
queue = Queue.Queue(0)

#Hpfeeds stuff for subscription
host = 'hpfriends.honeycloud.net'
port = 20000
ident = ''
secret = ''
channel = 'shiva.parsed'


def receive():
    hpc = hpfeeds.new(host, port, ident, secret)
    
    def on_message(ident, channel, payload):
        print "\nReceived from channel -> %s having ident -> %s at %s" % (channel, ident, datetime.datetime.now())
        data = cPickle.loads(str(payload))
        queue.put(data)  
        
    def on_error(payload):
        print "Error occured."
        for i in range(WORKERS):
            queue.put(None)
        hpc.stop()
                
    hpc.subscribe(channel)
    print "subscribed"
    try:
        hpc.run(on_message, on_error)
    except hpfeeds.FeedException, e:
        print e
        
def dumpspam():
    while 1:
        record = queue.get()
        if record is None:
            break
        else:           
            fname = record['s_id']
            data = cPickle.dumps(record)
            with open("spams/" + fname, 'wb') as fp:
                fp.write(data)
                fp.write("\n")

for i in range(WORKERS):
    t = threading.Thread(target=dumpspam, args=[])
    t.start()

try:
    receive()
except KeyboardInterrupt, e:
    for i in range(WORKERS):
        queue.put(None)
    sys.exit(0)
