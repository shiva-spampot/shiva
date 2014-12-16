#!/usr/bin/env python
""" corelate.py
Description - Picks up file(s) dumped by subscribe.py and saves data in the database after extracting and analyzing it.
Usage - python corelate.py
"""

import MySQLdb as mdb
import cPickle
import os
import ssdeep
import sys
import logging
import time
import datetime

path = "spams/"

def dbconnect():
    conn = None

    try:
        conn = mdb.connect (host = '127.0.0.1',
                            user = 'root',
                            passwd = 'password',
                            db = "Hpfeeds",
                            charset='utf8mb4',
                            use_unicode = True)
        conn.autocommit(True)
        cursor = conn.cursor()
        return cursor
    except mdb.Error, e:
        logging.critical("[-] Error (shivaconfig.py) - %d: %s" % (e.args[0], e.args[1]))

def queuereceiver():
    while True:
        files = os.listdir(path)
        if len(files) > 0:
            for spam_file in files:
                if os.stat(path + spam_file).st_size == 0:              # if somehow spam file size is zero
                    os.remove(path + spam_file)
                    continue
                
                with open(path + spam_file, "rb") as fp:
                    try:
                        record = cPickle.load(fp)
                    except Exception, e:
                        print "Error occured while unserializing. -> %s" % str(e)
                        continue
                if type(record) is dict:
                    conclude(record)

                try:
                    os.remove(path + spam_file)
                except Exception, e:
                    print "Error while deleting spam file. %s" % str(e)
        else:
            print "wake me up when something comes.....sleeping at %s" % datetime.datetime.now()
            time.sleep(600)
                        
def conclude(record):
    fetchfromdb = "SELECT `id`, `ssdeep`, `length` FROM `spam` WHERE 1"
    
    try:
        exeSql.execute(fetchfromdb)
    except mdb.Error, e:
        print e
        
    dbrecords = exeSql.fetchall()
    
    maxlen, minlen = int(record['len'] * 1.10), int(record['len'] * 0.90)
    count = 0
    
    for d_record in dbrecords:
        if d_record[2] >= minlen and d_record[2] <= maxlen:
            if record['s_id'] == d_record[0]:
                update(record, d_record[0])
            
            else:
                ratio = ssdeep.compare(record['ssdeep'], d_record[1])
                #if ratio >= 85:
                if (int(record['len']) <= 150 and ratio >=95) or (int(record['len']) > 150 and ratio >= 80):
                    update(record, d_record[0])
                else:
                    count += 1
        else:
            count += 1
    
    if count == len(dbrecords):
        insert(record)

def insert(record):
        
    # Inserting data in main db
    print "Inserting new spam!"
    #insert_spam = "INSERT INTO `spam`(`headers`, `to`, `from`, `subject`, `textMessage`, `htmlMessage`, `totalCounter`, `id`, `ssdeep`, `length`) VALUES('" + record['headers'] + "', '" + record['to'] + "', '" + record['from'] + "', '" + record['subject'] + "', '" + record['text'] + "', '" + record['html'] + "', '" + str(record['counter']) + "', '" + record['s_id'] + "', '" + record['ssdeep'] + "', '" + str(record['len']) + "')"
     
    insert_spam = "INSERT INTO `spam`(`headers`, `to`, `from`, `subject`, `textMessage`, `htmlMessage`, `totalCounter`, `id`, `ssdeep`, `length`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    values = str(record['headers']), str(record['to']), str(record['from']), str(record['subject']), str(record['text']), str(record['html']), str(record['counter']), str(record['s_id']), str(record['ssdeep']), str(record['len'])
    try:
        #exeSql.execute(insert_spam)
        exeSql.execute(insert_spam, values)
    except mdb.Error, e:
        print e
        return None
        
    #insert_sdate = "INSERT INTO sdate (`date`, `firstSeen`, `lastSeen`, `todaysCounter`) VALUES('" + str(record['date']) + "', '" + str(record['firstSeen']) + "', '" + str(record['lastSeen']) + "', '" + str(record['counter']) + "')"
    
    insert_sdate = "INSERT INTO sdate (`date`, `firstSeen`, `lastSeen`, `todaysCounter`) VALUES (%s, %s, %s, %s)"
    values = str(record['date']), str(record['firstSeen']), str(record['lastSeen']), str(record['counter'])
    try:
        exeSql.execute(insert_sdate, values)
    except mdb.Error, e:
        print e
        return None

    #insert_sdate_spam = "INSERT INTO sdate_spam (`spam_id`, `date_id`) VALUES('" + record['s_id'] + "', '" + str(exeSql.lastrowid) + "')"
    
    insert_sdate_spam = "INSERT INTO sdate_spam (`spam_id`, `date_id`) VALUES (%s, %s)"
    values = str(record['s_id']), str(exeSql.lastrowid)
    try:
        exeSql.execute(insert_sdate_spam, values)
    except mdb.Error, e:
        print e
        return None

    ip_list = record['sourceIP'].split(',')            
    for ip in ip_list:
        #insert_ip = "INSERT INTO ip (`date`, `sourceIP`) VALUES('" + str(record['date']) + "', '" + str(ip) + "' )"
        
        insert_ip = "INSERT INTO ip (`date`, `sourceIP`) VALUES (%s, %s)"
        values = str(record['date']), str(ip)
        try:
            exeSql.execute(insert_ip, values)
        except mdb.Error, e:
            print e
            return None

        #insert_ip_spam = "INSERT INTO ip_spam (`spam_id`, `ip_id`) VALUES('" + str(record['s_id']) + "', '" + str(exeSql.lastrowid) + "' )"
        
        insert_ip_spam = "INSERT INTO ip_spam (`spam_id`, `ip_id`) VALUES (%s, %s)"
        values = str(record['s_id']), str(exeSql.lastrowid)
        try:
            exeSql.execute(insert_ip_spam, values)
        except mdb.Error, e:
            print e
            return None    

    #insert_sensor = "INSERT INTO sensor (`date`, `sensorID`) VALUES('" + str(record['date']) + "', '" + record['sensorID'] + "' )"
    
    insert_sensor = "INSERT INTO sensor (`date`, `sensorID`) VALUES (%s, %s)"
    values = str(record['date']), record['sensorID']
    try:
        exeSql.execute(insert_sensor, values)
    except mdb.Error, e:
        print e
        return None

    #insert_sensor_spam = "INSERT INTO sensor_spam (`spam_id`, `sensor_id`) VALUES('" + str(record['s_id']) + "', '" + str(exeSql.lastrowid) + "' )"
    
    insert_sensor_spam = "INSERT INTO sensor_spam (`spam_id`, `sensor_id`) VALUES(%s, %s)"
    values = str(record['s_id']), str(exeSql.lastrowid)
    try:
        exeSql.execute(insert_sensor_spam, values)
    except mdb.Error, e:
        print e
        return None
        
    if len(record['links']) != 0:                                     # If links are present - insert into DB
        i = 0
        while i < len(record['links']):
            #insert_link = "INSERT INTO links (`date`, `hyperLink`, `spam_id` ) VALUES('" + str(record['date']) + "', '" + str(record['links'][i]) + "', '" + str(record['s_id']) + "')"
            
            insert_link = "INSERT INTO links (`date`, `hyperLink`, `spam_id` ) VALUES(%s, %s, %s)"
            values = str(record['date']), str(record['links'][i]), str(record['s_id'])
            i += 1
            try:
                exeSql.execute(insert_link, values)
            except mdb.Error, e:
                print e
                return None
    
    if int(record['relayed']) > 0:
        #insert_relay = "INSERT INTO `relay`(`date`, `firstRelayed`, `lastRelayed`, `totalRelayed`, `spam_id`, `sensorID`) VALUES ('" + str(record['date']) +"', '" + str(record['firstRelayed']) + "', '" + str(record['lastRelayed']) + "', '" + str(record['relayed']) + "', '" + str(record['s_id']) + "', '" + str(record['sensorID']) +"' )"
        
        insert_relay = "INSERT INTO `relay`(`date`, `firstRelayed`, `lastRelayed`, `totalRelayed`, `spam_id`, `sensorID`) VALUES (%s, %s, %s, %s, %s, %s)"
        values = str(record['date']), str(record['firstRelayed']), str(record['lastRelayed']), str(record['relayed']), str(record['s_id']), str(record['sensorID'])
        try:
            exeSql.execute(insert_relay, values)
        except mdb.Error, e:
            print e
            return None
        
    if len(record['attachmentFileMd5']) != 0:                    # If attachment is present - insert into DB
        i = 0
        while i < len(record['attachmentFileMd5']):
            
            fileName = str(record['s_id']) + "-a-" + str(record['attachmentFileName'][i])
            path = "attach/" + fileName
            with open(path, 'wb') as attachFile:
                attachFile.write(record['attachmentFile'][i])
                record['attachmentFile'][i] = path
            
            #insert_attachment = "INSERT INTO `attachment`(`date`, `md5`, `attachment_file_name`, `attachment_file_path`, `attachment_file_type`, `spam_id`) VALUES('" + str(record['date']) + "', '" + str(record['attachmentFileMd5'][i]) + "', '" + str(mdb.escape_string(record['attachmentFileName'][i])) + "', '" + str(mdb.escape_string(record['attachmentFile'][i])) + "', '" + str(os.path.splitext(mdb.escape_string(record['attachmentFileName'][i]))[1]) + "', '" + str(record['s_id']) + "')"
            
            insert_attachment = "INSERT INTO `attachment`(`date`, `md5`, `attachment_file_name`, `attachment_file_path`, `attachment_file_type`, `spam_id`) VALUES(%s, %s, %s, %s, %s, %s)"
            values = str(record['date']), str(record['attachmentFileMd5'][i]), str(mdb.escape_string(record['attachmentFileName'][i])), str(mdb.escape_string(record['attachmentFile'][i])), str(os.path.splitext(mdb.escape_string(record['attachmentFileName'][i]))[1]), str(record['s_id'])
            i = i + 1
            try:
                exeSql.execute(insert_attachment, values)
            except mdb.Error, e:
                print e
                return None

    if len(record['inlineFileMd5']) != 0:                                # If inline file is present - insert into DB
        i = 0
        while i < len(record['inlineFileMd5']):
            fileName = str(record['s_id']) + "-i-" + str(record['inlineFileName'][i])
            path = "attach/" + fileName
            with open(path, 'wb') as attachFile:
                attachFile.write(record['inlineFile'][i])
            
            #insert_inline = "INSERT INTO `inline`(`date`, `md5`, `inline_file_name`, `inline_file_path`, `spam_id` ) VALUES('" + str(record['date']) + "', '" + str(record['inlineFileMd5'][i]) + "', '" + str(mdb.escape_string(record['inlineFileName'][i])) + "', '" + str(mdb.escape_string(record['inlineFilePath'][i])) + "', '" + str(record['s_id']) + "')"
            
            insert_inline = "INSERT INTO `inline`(`date`, `md5`, `inline_file_name`, `inline_file_path`, `spam_id` ) VALUES(%s, %s, %s, %s, %s, %s)"
            values = str(record['date']), str(record['inlineFileMd5'][i]), str(mdb.escape_string(record['inlineFileName'][i])), str(mdb.escape_string(record['inlineFilePath'][i])), str(record['s_id'])
            i = i + 1
            try:
                exeSql.execute(insert_inline, values)
            except mdb.Error, e:
                print e
                return None
            
def update(record, spam_id):
    print "Updating record"
    date = 0                                                                                                                   
    #checkDate = "SELECT sdate.date FROM sdate JOIN sdate_spam ON (sdate.id = sdate_spam.date_id) WHERE sdate_spam.spam_id = '" + str(spam_id) + "' AND sdate.date = '" + str(record['date']) + "'"

    checkDate = "SELECT sdate.date FROM sdate JOIN sdate_spam ON (sdate.id = sdate_spam.date_id) WHERE sdate_spam.spam_id = %s AND sdate.date = %s"
    values = str(spam_id), str(record['date'])
    try:
        exeSql.execute(checkDate, values)
        if len(exeSql.fetchall()) >= 1:
            date = 1
    except mdb.Error, e:
        print e
        return None   

    if date == 0:
        #insert_sdate = "INSERT INTO sdate (`date`, `firstSeen`, `lastSeen`, `todaysCounter`) VALUES('" + str(record['date']) + "', '" + str(record['firstSeen']) + "', '" + str(record['lastSeen']) + "', '" + str(record['counter']) + "')"
        
        insert_sdate = "INSERT INTO sdate (`date`, `firstSeen`, `lastSeen`, `todaysCounter`) VALUES(%s, %s, %s, %s)"
        values = str(record['date']), str(record['firstSeen']), str(record['lastSeen']), str(record['counter'])
        try:
            exeSql.execute(insert_sdate, values)
        except mdb.Error, e:
            print e
            return None
        insert_sdate_spam = "INSERT INTO sdate_spam (`spam_id`, `date_id`) VALUES('" + str(spam_id) + "', '" + str(exeSql.lastrowid) + "')"
        try:
            exeSql.execute(insert_sdate_spam)
        except mdb.Error, e:
            print e
            return None

    else:
        #update_date = "UPDATE sdate JOIN sdate_spam ON (sdate.id = sdate_spam.date_id) SET sdate.lastSeen = '" + str(record['lastSeen'])+"', sdate.todaysCounter = sdate.todaysCounter + '" + str(record['counter']) + "' WHERE sdate_spam.spam_id = '" + str(spam_id) + "' AND sdate.date = '" + str(record['date'])+"'"
        
        update_date = "UPDATE sdate JOIN sdate_spam ON (sdate.id = sdate_spam.date_id) SET sdate.lastSeen = %s, sdate.todaysCounter = sdate.todaysCounter + %s WHERE sdate_spam.spam_id = %s AND sdate.date = %s"
        values = str(record['lastSeen']), str(record['counter']), str(spam_id), str(record['date'])
        try:
            exeSql.execute(update_date, values)
        except mdb.Error, e:
            print e
            return None
     
    # spam table totalCounter - bug fix
    #update_spam_counter = "UPDATE `spam` SET spam.totalCounter = spam.totalCounter + '" + str(record['counter']) + "' WHERE spam.id = '" + str(spam_id) + "'"
    
    update_spam_counter = "UPDATE `spam` SET spam.totalCounter = spam.totalCounter + %s WHERE spam.id = %s"
    values = str(record['counter']), str(spam_id)
    try:
        exeSql.execute(update_spam_counter, values)
    except mdb.Error, e:
        print e
        return None
    
    # Checking for IPs
    ip_list = str(record['sourceIP']).split(", ")
    for ip in ip_list:            
        ipStatus = 1
        #checkIP = "SELECT ip.sourceIP FROM ip JOIN ip_spam ON (ip.id = ip_spam.ip_id) WHERE ip_spam.spam_id = '" + str(spam_id) + "' AND ip.sourceIP = '" + str(ip) + "'"
        
        checkIP = "SELECT ip.sourceIP FROM ip JOIN ip_spam ON (ip.id = ip_spam.ip_id) WHERE ip_spam.spam_id = %s AND ip.sourceIP = %s"
        values = str(spam_id), str(ip)
        try:
            exeSql.execute(checkIP, values)
            if len(exeSql.fetchall()) >= 1:
                ipStatus = 1
        except mdb.Error, e:
            print e
            return None

        if ipStatus == 0:
            #insert_ip = "INSERT INTO ip (`date`, `sourceIP`) VALUES('" + str(record['date']) + "', '" + str(ip) + "' )"
            
            insert_ip = "INSERT INTO ip (`date`, `sourceIP`) VALUES(%s, %s)"
            values = str(record['date']), str(ip)
            try:
                exeSql.execute(insert_ip, values)
            except mdb.Error, e:
                print e
                return None

            insert_ip_spam = "INSERT INTO ip_spam (`spam_id`, `ip_id`) VALUES('" + str(spam_id) + "', '"+str(exeSql.lastrowid)+"')"

            try:
                exeSql.execute(insert_ip_spam)
            except mdb.Error, e:
                print e
                return None            
            
    # Checking for Sensor ID
    sensor_list = str(record['sensorID']).split(", ")
    for sensor in sensor_list:            
        sensorStatus = 1   
        #checkSensorID = "SELECT sensor.sensorID FROM sensor JOIN sensor_spam ON (sensor.id = sensor_spam.sensor_id) WHERE sensor_spam.spam_id = '" + str(spam_id) + "' AND sensor.sensorID = '" + str(sensor) + "'"
        
        checkSensorID = "SELECT sensor.sensorID FROM sensor JOIN sensor_spam ON (sensor.id = sensor_spam.sensor_id) WHERE sensor_spam.spam_id = %s AND sensor.sensorID = %s"
        values = str(spam_id), str(sensor)
        try:
           exeSql.execute(checkSensorID, values)
           if len(exeSql.fetchall()) >= 1:
                sensorStatus = 0
        except mdb.Error, e:
            print e

        if sensorStatus == 1:
            #insert_id = "INSERT INTO sensor (`date`, `sensorID`) VALUES('" + str(record['date']) + "', '" + str(sensor) + "' )"
            
            insert_id = "INSERT INTO sensor (`date`, `sensorID`) VALUES(%s, %s)"
            values = str(record['date']), str(sensor)
            try:
                exeSql.execute(insert_id, values)
            except mdb.Error, e:
                print e

            insert_id_spam = "INSERT INTO sensor_spam (`spam_id`, `sensor_id`) VALUES('" + str(spam_id) + "', '" + str(exeSql.lastrowid)+"')"

            try:
                exeSql.execute(insert_id_spam)
            except mdb.Error, e:
                print e
           
    # Checking for URLs
    for url in record['links']:
        urlstatus = 1
        #checkURL = "SELECT `hyperLink` FROM `links` WHERE `spam_id` = '" + str(spam_id) + "' AND `hyperLink` = '" + str(url) + "'"
        
        checkURL = "SELECT `hyperLink` FROM `links` WHERE `spam_id` = %s AND `hyperLink` = %s"
        values = str(spam_id), str(url)
        try:
            exeSql.execute(checkURL, values)
            records = exeSql.fetchall()
        except mdb.Error, e:
            print e
            return None
            
        if len(records) >= 1:
            urlstatus = 0
        
        if urlstatus == 1:
            #insert_url = "INSERT INTO `links`(`date`, `hyperLink`, `spam_id`) VALUES ('" + str(record['date']) + "', '" + str(url) + "', '" + str(spam_id) + "')"
            
            insert_url = "INSERT INTO `links`(`date`, `hyperLink`, `spam_id`) VALUES (%s, %s, %s)"
            values = str(record['date']), str(url), str(spam_id)
            try:
                exeSql.execute(insert_url, values)
            except mdb.Error, e:
                print e
                return None
          
    # Checking for attachments
    if len(record['attachmentFileMd5']) != 0:
        i = 0
        while i < len(record['attachmentFileMd5']):
            md5Status = 1
            #checkMd5 = "SELECT `md5` FROM `attachment` WHERE `spam_id` = '" + str(spam_id) + "' AND `md5` = '" + str(record['attachmentFileMd5'][i]) + "'"
            
            checkMd5 = "SELECT `md5` FROM `attachment` WHERE `spam_id` = %s AND `md5` = %s"
            values = str(spam_id), str(record['attachmentFileMd5'][i])
            try:
                exeSql.execute(checkMd5, values)
                records = exeSql.fetchall()
            except mdb.Error, e:
                print e
                return None
            
            if len(records) >= 1:
                md5Status = 0
                
            if md5Status == 1:
                fileName = str(record['s_id']) + "-a-" + str(record['attachmentFileName'][i])
                path = "attach/" + fileName
                with open(path, 'wb') as attachFile:
                    attachFile.write(record['attachmentFile'][i])
                    record['attachmentFile'][i] = path
                
                #insert_attachment = "INSERT INTO `attachment`(`date`, `md5`, `attachment_file_name`, `attachment_file_path`, `attachment_file_type`, `spam_id`) VALUES('" + str(record['date']) + "', '" + str(record['attachmentFileMd5'][i]) + "', '" + str(mdb.escape_string(record['attachmentFileName'][i].encode('utf-8'))) + "', '" + str(mdb.escape_string(record['attachmentFile'][i])) + "', '" + str(os.path.splitext(record['attachmentFileName'][i])[1].encode('utf-8')) + "', '" + str(spam_id) + "')"
                
                insert_attachment = "INSERT INTO `attachment`(`date`, `md5`, `attachment_file_name`, `attachment_file_path`, `attachment_file_type`, `spam_id`) VALUES(%s, %s, %s, %s, %s, %s)"
                values = str(record['date']), str(record['attachmentFileMd5'][i]), str(mdb.escape_string(record['attachmentFileName'][i].encode('utf-8'))), str(mdb.escape_string(record['attachmentFile'][i])), str(os.path.splitext(record['attachmentFileName'][i])[1].encode('utf-8')), str(spam_id)
                try:
                    exeSql.execute(insert_attachment, values)
                except mdb.Error, e:
                    print e
                    return None
            i = i + 1
    
    # Checking fo inline attachments
    if len(record['inlineFileMd5']) >= 1:
        i = 0
        while i < len(record['inlineFileMd5']):
            md5Status = 1
            #checkMd5 = "SELECT `md5` FROM `inline` WHERE `spam_id` = '" + str(spam_id) + "' AND `md5` = '" + str(record['inlineFileMd5'][i]) + "'"
            
            checkMd5 = "SELECT `md5` FROM `inline` WHERE `spam_id` = %s AND `md5` = %s"
            values = str(spam_id), str(record['inlineFileMd5'][i])
            try:
                exeSql.execute(checkMd5, values)
                records = exeSql.fetchall()
            except mdb.Error, e:
                print e
                return None
            
            if len(records) >= 1:
                md5Status = 0
                
            if md5Status == 1:
                fileName = str(record['s_id']) + "-i-" + str(record['inlineFileName'][i])
                path = "attach/" + fileName
                with open(path, 'wb') as attachFile:
                    attachFile.write(record['inlineFile'][i])
                
                #insert_inline = "INSERT INTO `inline`(`date`, `md5`, `inline_file_name`, `inline_file_path`, `spam_id` ) VALUES('" + str(record['date']) + "', '" + str(record['inlineFileMd5'][i]) + "', '" + str(mdb.escape_string(record['inlineFileName'][i])) + "', '" + str(mdb.escape_string(record['inlineFilePath'][i])) + "', '" + str(spam_id) + "')"
                
                insert_inline = "INSERT INTO `inline`(`date`, `md5`, `inline_file_name`, `inline_file_path`, `spam_id` ) VALUES(%s, %s, %s, %s, %s)"
                values = str(record['date']), str(record['inlineFileMd5'][i]), str(mdb.escape_string(record['inlineFileName'][i])), str(mdb.escape_string(record['inlineFilePath'][i])), str(spam_id)
                try:
                    exeSql.execute(insert_inline, values)
                except mdb.Error, e:
                    print e
                    return None
            i = i + 1
 
    # Last but not the least, updating relay table.
    if int(record['relayed']) > 0:
        relayDate = str(record['lastRelayed']).split(' ')[0]
        #checkRelayDate = "SELECT `id` FROM `relay` WHERE `spam_id` = '" + str(spam_id) + "' AND `date` = '" + str(relayDate) + "'"
        
        checkRelayDate = "SELECT `id` FROM `relay` WHERE `spam_id` = %s AND `date` = %s"
        values = str(spam_id), str(relayDate)
        try:
            exeSql.execute(checkRelayDate, values)
        except mdb.Error, e:
            print e
            return None
            
        if len(exeSql.fetchall()) >= 1:
            #update_relay = "UPDATE `relay` SET `lastRelayed` = '" + str(record['lastRelayed']) + "', totalRelayed = totalRelayed + '" + str(record['relayed']) + "' WHERE `spam_id` = '" + str(spam_id) + "' AND `date` = '" + str(relayDate) + "'"
            
            update_relay = "UPDATE `relay` SET `lastRelayed` = %s, totalRelayed = totalRelayed + %s WHERE `spam_id` = %s AND `date` = %s"
            values = str(record['lastRelayed']), str(record['relayed']), str(spam_id), str(relayDate)
            try:
                exeSql.execute(update_relay, values)
            except mdb.Error, e:
                print e
                return None
            
        else:
            #insert_relay = "INSERT INTO `relay`(`date`, `firstRelayed`, `lastRelayed`, `totalRelayed`, `spam_id`, `sensorID`) VALUES ('" + str(relayDate) + "', '" + str(record['firstRelayed']) + "', '" + str(record['lastRelayed']) + "', '" + str(record['relayed']) + "', '" + str(spam_id) + "', '" + str(record['sensorID']) + "')"
            
            insert_relay = "INSERT INTO `relay`(`date`, `firstRelayed`, `lastRelayed`, `totalRelayed`, `spam_id`, `sensorID`) VALUES (%s, %s, %s, %s, %s, %s)"
            values = str(relayDate), str(record['firstRelayed']), str(record['lastRelayed']), str(record['relayed']), str(spam_id), str(record['sensorID'])
            try:
                exeSql.execute(insert_relay, values)
            except mdb.Error, e:
                print e
                return None
            
if __name__ == '__main__':
    exeSql = dbconnect()
    try:
        queuereceiver()
    except KeyboardInterrupt:
        sys.exit(0)
