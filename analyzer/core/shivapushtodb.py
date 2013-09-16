#!/usr/bin/env python


import logging
import datetime
import subprocess
import os

import MySQLdb as mdb

import server
import shivadbconfig

def push():
    logging.info("[+]Inside shivapushtodb Module")
    exeSql = shivadbconfig.dbconnect()
    
    attachpath = server.shivaconf.get('analyzer', 'attachpath')
    inlinepath = server.shivaconf.get('global', 'inlinepath')    
    
    truncate = ['truncate attachments','truncate links', 'truncate sensors', 'truncate spam']
    for query in truncate:
        try:
            exeSql.execute(query)
        except Exception, e:
            logging.critical("[+]shivapushtodb.py error %s" % str(e))
            
    
    for record in server.QueueReceiver.records:
        logging.info("Records are %d" % len(server.QueueReceiver.records))

        insertSpam = "INSERT INTO `spam`(`id`, `ssdeep`, `to`, `from`, `textMessage`, `htmlMessage`, `subject`, `headers`, `sourceIP`, `sensorID`, `firstSeen`, `relayCounter`, `totalCounter`, `length`, `relayTime`) VALUES ('" + str(record['s_id']) + "', '" + str(record['ssdeep']) + "', '" + str(record['to']) + "', '" + str(record['from']) + "', '" + str(record['text']) + "', '" + str(record['html']) + "', '" + str(record['subject']) + "', '" + str(record['headers']) + "', '" + str(record['sourceIP']) + "', '" + str(record['sensorID']) + "', '" + str(record['firstSeen']) + "', '" + str(record['relayed']) + "', '" + str(record['counter']) + "', '" + str(record['len']) + "', '" + str(record['firstRelayed'])  + "')"

        try:
            exeSql.execute(insertSpam)
        except mdb.Error, e:
            logging.critical("[-] Error (shivapushtodb insert_spam) - %d: %s" % (e.args[0], e.args[1]))
            return None

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

                insertAttachment = "INSERT INTO `attachments`(`spam_id`, `file_name`, `attach_type`, `attachmentFileMd5`, `date`, `attachment_file_path`) VALUES ('" + str(record['s_id']) + "', '" + str(mdb.escape_string(record['attachmentFileName'][i])) + "', '" + 'attach' + "', '" + str(record['attachmentFileMd5'][i]) + "', '" + str(record['date']) + "', '" + str(path) +"')"

                try:
                    exeSql.execute(insertAttachment)
                    i += 1

                except mdb.Error, e:
                    logging.critical("[-] Error (shivapushtodb insert_attachment) - %d: %s" % (e.args[0], e.args[1]))
                    return None

        # Checking for inline attachment files
        if len(record['inlineFile']) > 0:
            i = 0
            while i < len(record['inlineFile']):
                fileName = str(record['s_id']) + "-i-" + str(record['inlineFileName'][i])
                path = inlinepath + fileName
                attachFile = open(path, 'wb')
                attachFile.write(record['inlineFile'][i])
                attachFile.close()
                insertInline = "INSERT INTO `attachments`(`spam_id`, `file_name`, `attach_type`, `attachmentFileMd5`, `date`, `attachment_file_path`) VALUES ('" + str(record['s_id']) + "', '" + str(mdb.escape_string(record['inlineFileName'][i])) + "', '" + 'inline' + "', '" + str(record['inlineFileMd5'][i]) + "', '" + str(record['date']) + "', '" + str(path) + "')"

                try:
                    exeSql.execute(insertInline)
                    i += 1
                except mdb.Error, e:
                    logging.critical("[-] Error (shivapushtodb insert_inline) - %d: %s" % (e.args[0], e.args[1]))
                    return None

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
                    return None


        # Extracting and saving name of the sensor
        insertSensor = "INSERT INTO `sensors` (`spam_id`, `sensorID`, `date`) VALUES ('" + str(record['s_id']) + "', '" + str(record['sensorID']) + "', '" + str(record['date']) + "')"

        try:
            exeSql.execute(insertSensor)
        except mdb.Error, e:
            logging.critical("[-] Error (shivapushtodb insert_sensor - %d: %s" % (e.args[0], e.args[1]))
            return None

    exeSql.close()
    del server.QueueReceiver.records[:]
    server.QueueReceiver.totalRelay = 0
    logging.info("[+]shivapushtodb Module: List and global list counter resetted.")
          
    subprocess.Popen(['python', os.path.dirname(os.path.realpath(__file__)) + '/shivamaindb.py'])
    logging.info("Shivamaindb called")
  
def sendfeed():
    logging.info("[+]shivapushtodb Module: Calling sendfeeds module.")
    subprocess.Popen(['python', os.path.dirname(os.path.realpath(__file__)) + '/hpfeeds/sendfeeds.py'])