#!/usr/bin/env python

import threading
import json
import os
import sys

import hpfeeds
import MySQLdb as mdb

import dbconfig

host = dbconfig.shivaconf.get('hpfeeds', 'host')
port = dbconfig.shivaconf.getint('hpfeeds', 'port')
ident = dbconfig.shivaconf.get('hpfeeds', 'ident')
secret = dbconfig.shivaconf.get('hpfeeds', 'secret')

path = {'raw_spam' : dbconfig.shivaconf.get('analyzer', 'rawspampath'), 
        'attach' : dbconfig.shivaconf.get('analyzer', 'attachpath')}


url_list, ip_list = [], []
channels = {'parsed': 'shiva.parsed', 
            'raw_spam': 'shiva.raw', 
            'attachments': 'shiva.attachments'}
lock = threading.Lock()


def send_urls():
    print "Sending URLs"
    for row in url_list:
        print "Sending URLs"
        d = {'type': 'url', 'id': row['id'], 'url': row['link']}
        data = json.dumps(d)
        with lock:
            hpc.publish(channels['parsed'], data)
            print "published."
    
def send_ips():
    print "Sending IPs."
    for row in ip_list:
        print "Sending IPs."
        d = {'type': 'ip', 'id': row['id'], 'ips': row['ips']}
        data = json.dumps(d)
        with lock:
            hpc.publish(channels['parsed'], data)
            print " published."
            
def send_raw():
    print "sending Raw"
    for f in os.listdir(path['raw_spam']):
        print "sending raw"
        spam_id = f.split('-')[0]
        ip = f.split('-')[-2]
        spamfile = open(path['raw_spam']+f, 'r').read()
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
            attachment = open(path['attach']+f, 'r').read()
            d = {'id': spam_id, 'attachment': attachment, 'name': name}
            data = json.dumps(d)
            with lock:
                hpc.publish(channels['attachments'], data)
                print "Published."
        except:
            print "[-]shivamaindb: Error while publishing attachment."

    
def main():
    getdata()
    
    try:
        url_thread = threading.Thread(target = send_urls, args = [])
        raw_thread = threading.Thread(target = send_raw, args = [])
        attach_thread = threading.Thread(target = send_attach, args = [])
        ip_thread = threading.Thread(target = send_ips, args = [])
    except Exception, e:
        print "[-]shivamaindb: Error. %s" % e
        sys.exit(1)
     
    try: 
        url_thread.run()
        raw_thread.run()
        attach_thread.run()
        ip_thread.run()
    except Exception, e:
        print e
    
    while url_thread.isAlive() or raw_thread.isAlive() or attach_thread.isAlive() or ip_thread.isAlive():
        pass


def getdata():
    """This function is used to fetch the IPs and URLs from the temporary database.
    This data is sent to hpfeeds.
    """
    urlquery = "SELECT `spam_id`, `hyperlink` FROM `links` WHERE 1"
    try:
        exeSql.execute(urlquery)
    except mdb.Error, e:
        print "[-]shivamaindb: Error while fetching links.  %s" % e
        
    urls = exeSql.fetchall()
    for record in urls:
        url = {'id': record[0], 'link': record[1]}
        url_list.append(url)
        
    ipquery = "SELECT `id`, `sourceIP` FROM `spam` WHERE 1"
    try:
        exeSql.execute(ipquery)
    except mdb.Error, e:
        print "[-]shivamaindb: Error while fetching IPs. %s" % e
         
    ips = exeSql.fetchall()
    for record in ips:
        ip = {'id': record[0], 'ips': record[1]}
        ip_list.append(ip)
        
     
     
if __name__ == '__main__':
   hpc = hpfeeds.new(host, port, ident, secret)
   exeSql = dbconfig.dbconnect()
   main()
