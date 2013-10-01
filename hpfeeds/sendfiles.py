#!/usr/bin/env python

import threading
import json
import os
import sys
import ConfigParser

import hpfeeds

confpath = os.path.dirname(os.path.realpath(__file__)) + "/../../../../../../shiva.conf"
shivaconf = ConfigParser.ConfigParser()
shivaconf.read(confpath)

host = shivaconf.get('hpfeeds', 'host')
port = shivaconf.getint('hpfeeds', 'port')
ident = shivaconf.get('hpfeeds', 'ident')
secret = shivaconf.get('hpfeeds', 'secret')

path = {'raw_spam' : shivaconf.get('analyzer', 'rawspampath'), 
        'attach' : shivaconf.get('analyzer', 'attachpath')}

channels = {'raw_spam': 'shiva.raw', 
            'attachments': 'shiva.attachments'}
lock = threading.Lock()
            
def send_raw():
    print "sending Raw"
    for f in os.listdir(path['raw_spam']):
        print "sending raw"
        spam_id = f.split('-')[0]
        ip = f.split('-')[-2]
        with open(path['raw_spam']+f, 'r').read() as spamfile:
            d = {'id': spam_id, 'spamfile': spamfile, 'ip': ip, 'name': f}
            data = json.dumps(d)
            with lock:
                hpc.publish(channels['raw_spam'], data)
                print "Published."
            
def send_attach():
    print "sending attachment"
    for f in os.listdir(path['attach']):
        print "Sending attachment."
        try:
            spam_id = f.split('-')[0]
            name = f.split('-')[1]
            with open(path['attach']+f, 'r').read() as attachment:
                d = {'id': spam_id, 'attachment': attachment, 'name': name}
                data = json.dumps(d)
                with lock:
                    hpc.publish(channels['attachments'], data)
                    print "Published."
        except:
            print "[-]shivamaindb: Error while publishing attachment."
    
def main():    
    try:
        raw_thread = threading.Thread(target = send_raw, args = []).run()
        attach_thread = threading.Thread(target = send_attach, args = []).run()
    except Exception, e:
        print "[-]shivamaindb: Error. %s" % e
        sys.exit(1)
    
    while raw_thread.isAlive() or attach_thread.isAlive():
        pass

if __name__ == '__main__':
   hpc = hpfeeds.new(host, port, ident, secret)
   main()
