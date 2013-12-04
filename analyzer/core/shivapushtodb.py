#!/usr/bin/env python


import logging
import datetime
import subprocess
import os
import sys
import json
import cPickle
import copy

import MySQLdb as mdb

import server
import shivadbconfig
import shivanotifyerrors

def push():
    logging.info("[+]Inside shivapushtodb Module")
    notify = server.shivaconf.getboolean('notification', 'enabled')
    exeSql = shivadbconfig.dbconnect()
    
    attachpath = server.shivaconf.get('analyzer', 'attachpath')
    inlinepath = server.shivaconf.get('analyzer', 'inlinepath')    
    
    truncate = ['truncate attachments','truncate links', 'truncate sensors', 'truncate spam']
    for query in truncate:
        try:
            exeSql.execute(query)
        except Exception, e:
            logging.critical("[-] Error (shivapushtodb) truncate %s" % str(e))
            if notify is True:
                shivanotifyerrors.notifydeveloper("[-] Error (Module shivapushtodb.py) - truncate %s" % e)
            
    
    for record in server.QueueReceiver.deep_records:
        logging.info("Records are %d" % len(server.QueueReceiver.deep_records))

        insertSpam = "INSERT INTO `spam`(`id`, `ssdeep`, `to`, `from`, `textMessage`, `htmlMessage`, `subject`, `headers`, `sourceIP`, `sensorID`, `firstSeen`, `relayCounter`, `totalCounter`, `length`, `relayTime`) VALUES ('" + str(record['s_id']) + "', '" + str(record['ssdeep']) + "', '" + str(record['to']) + "', '" + str(record['from']) + "', '" + str(record['text']) + "', '" + str(record['html']) + "', '" + str(record['subject']) + "', '" + str(record['headers']) + "', '" + str(record['sourceIP']) + "', '" + str(record['sensorID']) + "', '" + str(record['firstSeen']) + "', '" + str(record['relayed']) + "', '" + str(record['counter']) + "', '" + str(record['len']) + "', '" + str(record['firstRelayed'])  + "')"

        try:
            exeSql.execute(insertSpam)
        except mdb.Error, e:
            logging.critical("[-] Error (shivapushtodb insert_spam) - %d: %s" % (e.args[0], e.args[1]))
            if notify is True:
                shivanotifyerrors.notifydeveloper("[-] Error (Module shivapushtodb.py) - insertSpam %s" % e)

        # Checking for attachments and dumping into directory, if any. Also storing information in database.
        if len(record['attachmentFile']) > 0:
            i = 0
            while i < len(record['attachmentFile']):
                fileName = str(record['s_id']) + "-a-" + str(record['attachmentFileName'][i])
                path = attachpath + fileName
                attachFile = open(path, 'wb')
                attachFile.write(record['attachmentFile'][i])
                attachFile.close()
                record['attachmentFile'][i] = path
                insertAttachment = "INSERT INTO `attachments`(`spam_id`, `file_name`, `attach_type`, `attachmentFileMd5`, `date`, `attachment_file_path`) VALUES ('" + str(record['s_id']) + "', '" + str(mdb.escape_string(record['attachmentFileName'][i])) + "', '" + 'attach' + "', '" + str(record['attachmentFileMd5'][i]) + "', '" + str(record['date']) + "', '" + str(mdb.escape_string(path)) +"')"
              
                try:
                    exeSql.execute(insertAttachment)
                    i += 1

                except mdb.Error, e:
                    logging.critical("[-] Error (shivapushtodb insert_attachment) - %d: %s" % (e.args[0], e.args[1]))
                    if notify is True:
                        shivanotifyerrors.notifydeveloper("[-] Error (Module shivapushtodb.py) - insertAttachment %s" % e)

        # Checking for inline attachment files
        if len(record['inlineFile']) > 0:
            i = 0
            while i < len(record['inlineFile']):
                fileName = str(record['s_id']) + "-i-" + str(record['inlineFileName'][i])
                path = inlinepath + fileName
                attachFile = open(path, 'wb')
                attachFile.write(record['inlineFile'][i])
                attachFile.close()
                insertInline = "INSERT INTO `attachments`(`spam_id`, `file_name`, `attach_type`, `attachmentFileMd5`, `date`, `attachment_file_path`) VALUES ('" + str(record['s_id']) + "', '" + str(mdb.escape_string(record['inlineFileName'][i])) + "', '" + 'inline' + "', '" + str(record['inlineFileMd5'][i]) + "', '" + str(record['date']) + "', '" + str(mdb.escape_string(path)) + "')"

                try:
                    exeSql.execute(insertInline)
                    i += 1
                except mdb.Error, e:
                    logging.critical("[-] Error (shivapushtodb insert_inline) - %d: %s" % (e.args[0], e.args[1]))
                    if notify is True:
                        shivanotifyerrors.notifydeveloper("[-] Error (Module shivapushtodb.py) - insertInline %s" % e)

        # Checking for links in spams and storing them
        if len(record['links']) > 0:
            i = 0
            for link in record['links']:
                insertLink = "INSERT INTO `links` (`spam_id`, `hyperlink`, `date`) VALUES ('" + str(record['s_id']) + "', '" + str(link) + "', '" + str(record['date']) + "')"

                try:
                    exeSql.execute(insertLink)
                    i += 1
                except mdb.Error, e:
                    logging.critical("[-] Error (shivapushtodb insert_link) - %d: %s" % (e.args[0], e.args[1]))
                    if notify is True:
                        shivanotifyerrors.notifydeveloper("[-] Error (Module shivapushtodb.py) - insertLink %s" % e)


        # Extracting and saving name of the sensor
        insertSensor = "INSERT INTO `sensors` (`spam_id`, `sensorID`, `date`) VALUES ('" + str(record['s_id']) + "', '" + str(record['sensorID']) + "', '" + str(record['date']) + "')"

        try:
            exeSql.execute(insertSensor)
        except mdb.Error, e:
            logging.critical("[-] Error (shivapushtodb insert_sensor - %d: %s" % (e.args[0], e.args[1]))
            if notify is True:
                shivanotifyerrors.notifydeveloper("[-] Error (Module shivapushtodb.py) - insertSensor %s" % e)
          
    subprocess.Popen(['python', os.path.dirname(os.path.realpath(__file__)) + '/shivamaindb.py'])
    logging.info("Shivamaindb called")
    exeSql.close()
  
def sendfeed():
    sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/hpfeeds/")
    import hpfeeds    
    
    host = server.shivaconf.get('hpfeeds', 'host')
    port = server.shivaconf.getint('hpfeeds', 'port')
    ident = server.shivaconf.get('hpfeeds', 'ident')
    secret = server.shivaconf.get('hpfeeds', 'secret')
    channel = {"parsed": "shiva.parsed", "ip_url": "shiva.ip.url"}
    
    try:
        hpc = hpfeeds.new(host, port, ident, secret)
    except Exception, e:
        logging.critical("Cannot connect. %s" % e)
        
    for record in server.QueueReceiver.deep_records:
        try:
            data = cPickle.dumps(record)
            hpc.publish(channel["parsed"], data)
            logging.info("Record sent.")
        except Exception, e:
            logging.critical("[-] Error (shivapushtodb parsed) in publishing to hpfeeds. %s" % e)   
    
        if len(record['links']) > 0:
            for link in record['links']:
                try:
                    data = {"id": record['s_id'], "url": link}
                    data = json.dumps(data)
                    hpc.publish(channel["ip_url"], data)
                except Exception, e:
                    logging.critical("[-] Error (shivapushtodb link) in publishing to hpfeeds. %s" % e)
                
        ip_list = record['sourceIP'].split(',')            
        for ip in ip_list:
            try:
                data = {"id": record['s_id'], "source_ip": ip}
                data = json.dumps(data)
                hpc.publish(channel["ip_url"], data)
            except Exception, e:
                logging.critical("[-] Error (shivapushtodb ip) in publishing to hpfeeds. %s" % e)
                
    logging.info("[+]shivapushtodb Module: Calling sendfiles module.")
    subprocess.Popen(['python', os.path.dirname(os.path.realpath(__file__)) + '/hpfeeds/sendfiles.py'])
        
def cleanup():
    server.QueueReceiver.deep_records = copy.deepcopy(server.QueueReceiver.records)
    del server.QueueReceiver.records[:]
    server.QueueReceiver.totalRelay = 0
    logging.info("[+]shivapushtodb Module: List and global list counter resetted.")
    
def getspammeremails():
    mainDb = shivadbconfig.dbconnectmain()
    notify = server.shivaconf.getboolean('notification', 'enabled')
    
    whitelist = "SELECT `recipients` from `whitelist`"
    
    try:
        mainDb.execute(whitelist)
        record = mainDb.fetchone()
        if ((record is None) or (record[0] is None)):
            server.whitelist_ids['spammers_email'] = []
            
           
        else:
            server.whitelist_ids['spammers_email'] = (record[0].encode('utf-8')).split(",")[-50:]
            server.whitelist_ids['spammers_email'] = list(set(server.whitelist_ids['spammers_email']))
            
                
        logging.info("[+] Pushtodb Module: whitelist recipients:")
        for key, value in server.whitelist_ids.items():
            logging.info("key: %s, value: %s" % (key, value))
            
        mainDb.close()
        
    except mdb.Error, e:
        logging.critical("[-] Error (Module shivapushtodb.py) - some issue obtaining whitelist: %s" % e)
        if notify is True:
            shivanotifyerrors.notifydeveloper("[-] Error (Module shivapushtodb.py) - getspammeremails %s" % e)
                
    for record in server.QueueReceiver.deep_records:
        try:
            if record['counter'] < 30:
                logging.info("type: %s, record to values: %s" % (type(record['to']), record['to']))
                #server.spammers_email.extend(record['to'].split(","))
                #server.spammers_email = list(set(server.spammers_email))
                
                #server.whitelist_ids[record['s_id']].append(record['to'].split(","))
                server.whitelist_ids[record['s_id']] = record['to'].split(",")

                
                for key, value in server.whitelist_ids.items():
                    logging.info("New record - key: %s, value: %s" % (key, value))
                                
        except Exception, e:
            if notify is True:
                shivanotifyerrors.notifydeveloper("[-] Error (Module shivapushtodb.py) - extending whitelist %s" % e)
