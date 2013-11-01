#!/usr/bin/env python

import threading
import json
import os
import sys
import ConfigParser
import shutil
import base64

import hpfeeds

confpath = os.path.dirname(os.path.realpath(__file__)) + "/../../../../../../shiva.conf"
shivaconf = ConfigParser.ConfigParser()
shivaconf.read(confpath)

host = shivaconf.get('hpfeeds', 'host')
port = shivaconf.getint('hpfeeds', 'port')
ident = shivaconf.get('hpfeeds', 'ident')
secret = shivaconf.get('hpfeeds', 'secret')

path = {'raw_spam' : shivaconf.get('analyzer', 'rawspampath'), 
        'attach' : shivaconf.get('analyzer', 'attachpath'),
        'hpfeedspam' : shivaconf.get('hpfeeds', 'hpfeedspam'),
        'hpfeedattach' : shivaconf.get('hpfeeds', 'hpfeedattach')}

channels = {'raw_spam': 'shiva.raw', 
            'attachments': 'shiva.attachments'}
lock = threading.Lock()
            
def send_raw():
    files = [f for f in os.listdir(path['raw_spam']) if os.path.isfile(os.path.join(path['raw_spam'], f))]

    if len(files) > 0:
        for f in files:
            print "sending raw spam on hpfeeds channel shiva.raw"
            spam_id = f.split('-')[0]
            ip = f.split('-')[-2]
            
            with open(path['raw_spam']+f) as fp:
                spamfile = fp.read()
            
            d = {'id': spam_id, 'spamfile': spamfile, 'ip': ip, 'name': f}
            data = json.dumps(d)
            with lock:
                hpc.publish(channels['raw_spam'], data)
                print "Raw Published"
            
            shutil.move(path['raw_spam']+f, path['hpfeedspam'])
    else:
        print "nothing to send on hpfeeds channel shiva.raw"
                
            
def send_attach():
    files = [f for f in os.listdir(path['attach']) if os.path.isfile(os.path.join(path['attach'], f))]
    
    if len(files) > 0:
        for f in files:
            print "sending attachment %s on hpfeeds channel shiva.attachments" % f
            spam_id = f.split('-')[0]
            name = f.split('-')[2]
            
            with open(path['attach']+f) as fp:
                attachment = base64.b64encode(fp.read())
            
            d = {'id': spam_id, 'attachment': attachment, 'name': name}
            data = json.dumps(d)
            with lock:
                hpc.publish(channels['attachments'], data)
                print "[+] Attachment Published"
            
            shutil.move(path['attach']+f, path['hpfeedattach'])
    else:
        print "nothing to send on hpfeeds channel shiva.attachments"
    
def main():    
    try:
        raw_thread = threading.Thread(target = send_raw, args = []).run()
        attach_thread = threading.Thread(target = send_attach, args = []).run()
    except Exception, e:
        print "[-] shivasendfiles main: Error. %s" % e
        sys.exit(1)
    
    while raw_thread.isAlive() or attach_thread.isAlive():
        pass

if __name__ == '__main__':
   hpc = hpfeeds.new(host, port, ident, secret)
   main()
