#!/usr/bin/env python

from datetime import date
import time
import sys
import os

import server
import shivadbconfig
import shivanotifyerrors

import ssdeep
import MySQLdb as mdb


def main():
    fetchfromtempdb = "SELECT `id`, `ssdeep`, `length` FROM `spam` WHERE 1"
    fetchfrommaindb = "SELECT `id`, `ssdeep`, `length` FROM `spam` WHERE 1"
    
    
    
    try:
        tempDb.execute(fetchfromtempdb)
        mainDb.execute(fetchfrommaindb)
    except mdb.Error, e:
        print e
        if notify is True:
            shivanotifyerrors.notifydeveloper("[-] Error (Module shivamaindb.py) - executing fetchfromdb %s" % e)
        
    temprecords = tempDb.fetchall()
    mainrecords = mainDb.fetchall()
    
    for t_record in temprecords:
        maxlen, minlen = int(t_record[2] * 1.10), int(t_record[2] * 0.90)
        count = 0
        
        for m_record in mainrecords:
            if m_record[2] >= minlen and m_record[2] <= maxlen:
                if t_record[0] == m_record[0]:
                    update(t_record[0], m_record[0])
                
                else:
                    ratio = ssdeep.compare(t_record[1], m_record[1])
                    if ratio >= 80:
                        update(t_record[0], m_record[0])
                    else:
                        count += 1
            else:
                count += 1
        
        if count == len(mainrecords):
            insert(t_record[0])
            
    # At last update whitelist recipients
    group_concat_max_len = "SET SESSION group_concat_max_len = 20000"
    whitelist = "INSERT INTO `whitelist` (`id`, `recipients`) VALUES ('1', (SELECT GROUP_CONCAT(DISTINCT `to`) FROM `spam` WHERE `totalCounter` < 30)) ON DUPLICATE KEY UPDATE `recipients` = (SELECT GROUP_CONCAT(DISTINCT `to`) FROM `spam` WHERE `totalCounter` < 30)"
  
    try:
        mainDb.execute(group_concat_max_len)
        mainDb.execute(whitelist)
    except mdb.Error, e:
        print e
        if notify is True:
            shivanotifyerrors.notifydeveloper("[-] Error (Module shivamaindb.py) - executing mainDb %s" % e)
    
def insert(spam_id):
    
    mailFields = {'s_id':'', 'ssdeep':'', 'to':'', 'from':'', 'text':'', 'html':'', 'subject':'', 'headers':'', 'sourceIP':'', 'sensorID':'', 'firstSeen':'', 'relayCounter':'', 'relayTime':'', 'count':0, 'len':'', 'inlineFileName':[], 'inlineFilePath':[], 'inlineFileMd5':[], 'attachmentFileName':[], 'attachmentFilePath':[], 'attachmentFileMd5':[], 'links':[],  'date': '' }
    
    spam = "SELECT `id`, `ssdeep`, `to`, `from`, `textMessage`, `htmlMessage`, `subject`, `headers`, `sourceIP`, `sensorID`, `firstSeen`, `relayCounter`, `relayTime`, `totalCounter`, `length` FROM `spam` WHERE `id` = '" + str(spam_id) + "'"
    
    attachments = "SELECT `id`, `spam_id`, `file_name`, `attach_type`, `attachmentFileMd5`, `date`, `attachment_file_path` FROM `attachments` WHERE `spam_id` = '" + str(spam_id) + "'"
    
    url = "SELECT `id`, `spam_id`, `hyperlink`, `date` FROM `links` WHERE `spam_id` = '" + str(spam_id) + "'"
    
    sensor = "SELECT `id`, `sensorID` FROM `spam` WHERE `id` = '" + str(spam_id) + "'"
    
    try:
        # Saving 'spam' table's data
        tempDb.execute(spam)
        spamrecord = tempDb.fetchone()
        if spamrecord:
            mailFields['s_id'], mailFields['ssdeep'], mailFields['to'], mailFields['from'], mailFields['text'], mailFields['html'], mailFields['subject'], mailFields['headers'], mailFields['sourceIP'], mailFields['sensorID'], mailFields['firstSeen'], mailFields['relayCounter'], mailFields['relayTime'], mailFields['count'], mailFields['len'] = spamrecord
            
            mailFields['date'] = str(mailFields['firstSeen']).split(' ')[0]
            # Saving 'attachments' table's data
            tempDb.execute(attachments)
            attachrecords = tempDb.fetchall()
            for record in attachrecords:
                
                if str(record[3]) == 'attach':  # Note: record[3] denotes 'attach_type' field in table. Could be 'attach' or 'inline'
                    mailFields['attachmentFileName'].append(record[2])
                    mailFields['attachmentFileMd5'].append(record[4])
                    mailFields['attachmentFilePath'].append(record[6])
                    
                elif str(record[3]) == 'inline':
                    mailFields['inlineFileName'].append(record[2])
                    mailFields['inlineFileMd5'].append(record[4])
                    mailFields['inlineFilePath'].append(record[6])
            
            # Saving 'links' table's data
            tempDb.execute(url)
            urlrecords = tempDb.fetchall()
            for record in urlrecords:
                mailFields['links'].append(record[2])
            
            # Saving 'sensor' table's data
            tempDb.execute(sensor)
            sensorrecords = tempDb.fetchone()
            mailFields['sensorID'] = sensorrecords[1]
            
            
            # Inserting data in main db
            insert_spam = "INSERT INTO `spam`(`headers`, `to`, `from`, `subject`, `textMessage`, `htmlMessage`, `totalCounter`, `id`, `ssdeep`, `length`) VALUES('" + mailFields['headers'] + "', '" + mailFields['to'] + "', '" + mailFields['from'] + "', '" + mailFields['subject'] + "', '" + mailFields['text'] + "', '" + mailFields['html'] + "', '" + str(mailFields['count']) + "', '" + mailFields['s_id'] + "', '" + mailFields['ssdeep'] + "', '" + str(mailFields['len']) + "')"
                        
            try:
                mainDb.execute(insert_spam)
            except mdb.Error, e:
                print e
                if notify is True:
                    shivanotifyerrors.notifydeveloper("[-] Error (Module shivamaindb.py) - executing insert_spam %s" % e)
                
            insert_sdate = "INSERT INTO sdate (`date`, `firstSeen`, `lastSeen`, `todaysCounter`) VALUES('" + str(mailFields['date']) + "', '" + str(mailFields['firstSeen']) + "', '" + str(mailFields['firstSeen']) + "', '" + str(mailFields['count']) + "')"
            try:
                mainDb.execute(insert_sdate)
            except mdb.Error, e:
                print e
                if notify is True:
                    shivanotifyerrors.notifydeveloper("[-] Error (Module shivamaindb.py) - executing insert_sdate %s" % e)

            insert_sdate_spam = "INSERT INTO sdate_spam (`spam_id`, `date_id`) VALUES('" + mailFields['s_id'] + "', '" + str(mainDb.lastrowid) + "')"
            
            try:
                mainDb.execute(insert_sdate_spam)
            except mdb.Error, e:
                print e
                if notify is True:
                    shivanotifyerrors.notifydeveloper("[-] Error (Module shivamaindb.py) - executing insert_sdate_spam %s" % e)

            ip_list = mailFields['sourceIP'].split(',')            
            for ip in ip_list:
                insert_ip = "INSERT INTO ip (`date`, `sourceIP`) VALUES('" + str(mailFields['date']) + "', '" + str(ip) + "' )"
                try:
                    mainDb.execute(insert_ip)
                except mdb.Error, e:
                    print e
                    if notify is True:
                        shivanotifyerrors.notifydeveloper("[-] Error (Module shivamaindb.py) - executing insert_ip %s" % e)

                insert_ip_spam = "INSERT INTO ip_spam (`spam_id`, `ip_id`) VALUES('" + str(mailFields['s_id']) + "', '" + str(mainDb.lastrowid) + "' )"
                try:
                    mainDb.execute(insert_ip_spam)
                except mdb.Error, e:
                    print e
                    if notify is True:
                        shivanotifyerrors.notifydeveloper("[-] Error (Module shivamaindb.py) - executing insert_ip_spam %s" % e)    

            insert_sensor = "INSERT INTO sensor (`date`, `sensorID`) VALUES('" + str(mailFields['date']) + "', '" + mailFields['sensorID'] + "' )"
            try:
                mainDb.execute(insert_sensor)
            except mdb.Error, e:
                print e
                if notify is True:
                    shivanotifyerrors.notifydeveloper("[-] Error (Module shivamaindb.py) - executing insert_sensor %s" % e)

            insert_sensor_spam = "INSERT INTO sensor_spam (`spam_id`, `sensor_id`) VALUES('" + str(mailFields['s_id']) + "', '" + str(mainDb.lastrowid) + "' )"
            try:
                mainDb.execute(insert_sensor_spam)
            except mdb.Error, e:
                print e
                if notify is True:
                    shivanotifyerrors.notifydeveloper("[-] Error (Module shivamaindb.py) - executing insert_sensor_spam %s" % e)
                
            if len(mailFields['links']) != 0:                                     # If links are present - insert into DB
                i = 0
                while i < len(mailFields['links']):
                    insert_link = "INSERT INTO links (`date`, `hyperLink`, `spam_id` ) VALUES('" + str(mailFields['date']) + "', '" + str(mailFields['links'][i]) + "', '" + str(mailFields['s_id']) + "')"
                    i += 1
                    try:
                        mainDb.execute(insert_link)
                    except mdb.Error, e:
                        print e
                        if notify is True:
                            shivanotifyerrors.notifydeveloper("[-] Error (Module shivamaindb.py) - executing insert_link %s" % e)
            
            if int(mailFields['relayCounter']) > 0:
                insert_relay = "INSERT INTO `relay`(`date`, `firstRelayed`, `lastRelayed`, `totalRelayed`, `spam_id`, `sensorID`) VALUES ('" + str(mailFields['date']) +"', '" + str(mailFields['relayTime']) + "', '" + str(mailFields['relayTime']) + "', '" + str(mailFields['relayCounter']) + "', '" + str(mailFields['s_id']) + "', '" + str(mailFields['sensorID']) +"' )"
                
                
                try:
                    mainDb.execute(insert_relay)
                except mdb.Error, e:
                    print e
                    if notify is True:
                        shivanotifyerrors.notifydeveloper("[-] Error (Module shivamaindb.py) - executing insert_relay %s" % e)
                
            if len(mailFields['attachmentFileMd5']) != 0:                    # If attachment is present - insert into DB
                i = 0
                while i < len(mailFields['attachmentFileMd5']):
                    insert_attachment = "INSERT INTO `attachment`(`date`, `md5`, `attachment_file_name`, `attachment_file_path`, `attachment_file_type`, `spam_id`) VALUES('" + str(mailFields['date']) + "', '" + str(mailFields['attachmentFileMd5'][i]) + "', '" + str(mdb.escape_string(mailFields['attachmentFileName'][i].encode('utf-8'))) + "', '" + str(mdb.escape_string(mailFields['attachmentFilePath'][i].encode('utf-8'))) + "', '" + str(os.path.splitext(mdb.escape_string(mailFields['attachmentFileName'][i].encode('utf-8')))[1]) + "', '" + str(mailFields['s_id']) + "')"
                    i = i + 1
                    try:
                        mainDb.execute(insert_attachment)
                    except mdb.Error, e:
                        print e
                        if notify is True:
                            shivanotifyerrors.notifydeveloper("[-] Error (Module shivamaindb.py) - executing insert_attachmentFileMd5 %s" % e)

            if len(mailFields['inlineFileMd5']) != 0:                                # If inline file is present - insert into DB
                i = 0
                while i < len(mailFields['inlineFileMd5']):
                    insert_inline = "INSERT INTO `inline`(`date`, `md5`, `inline_file_name`, `inline_file_path`, `spam_id` ) VALUES('" + str(mailFields['date']) + "', '" + str(mailFields['inlineFileMd5'][i]) + "', '" + str(mdb.escape_string(mailFields['inlineFileName'][i].encode('utf-8'))) + "', '" + str(mdb.escape_string(mailFields['inlineFilePath'][i].encode('utf-8'))) + "', '" + str(mailFields['s_id']) + "')"
                    i = i + 1
                    try:
                        mainDb.execute(insert_inline)
                    except mdb.Error, e:
                        print e
                        if notify is True:
                            shivanotifyerrors.notifydeveloper("[-] Error (Module shivamaindb.py) - executing insert_inline %s" % e)

    except mdb.Error, e:
        print e
        if notify is True:
            shivanotifyerrors.notifydeveloper("[-] Error (Module shivamaindb.py) - executing insert_spamid %s" % e)
        
    
def update(tempid, mainid):
    mailFields = {'sourceIP':'', 'sensorID':'', 'firstSeen':'', 'relayCounter':'', 'relayTime':'', 'count':0, 'inlineFileName':[], 'inlineFilePath':[], 'inlineFileMd5':[], 'attachmentFileName':[], 'attachmentFilePath':[], 'attachmentFileMd5':[], 'links':[],  'date': '', 'to': ''}
    
    tempurls = "SELECT `hyperlink` FROM `links` WHERE `spam_id` = '" + str(tempid) + "'"
    tempattachs = "SELECT `file_name`, `attachment_file_path`, `attach_type`, `attachmentFileMd5` FROM `attachments` WHERE `spam_id` = '" + str(tempid) + "'"
    tempsensors = "SELECT `sensorID` FROM `sensors` WHERE `spam_id` = '" + str(tempid) + "'"
    tempspam = "SELECT `firstSeen`, `relayCounter`, `relayTime`, `sourceIP`, `totalCounter`, `to` FROM `spam` WHERE `id` = '" + str(tempid) + "'"
    
    try:
        tempDb.execute(tempurls)
        records = tempDb.fetchall()
        
        for record in records:
            mailFields['links'].append(record[0])
            
            
        tempDb.execute(tempattachs)
        records = None          # To make sure that in case following query fails, we don't end up updating values from last query.
        records = tempDb.fetchall()
        
        for record in records:
            if record[2] == 'attach':           # Note: record[2] denotes 'attach_type' field in table. Could be either 'attach' or 'inline'
                mailFields['attachmentFileName'].append(record[0])
                mailFields['attachmentFileMd5'].append(record[3])
                mailFields['attachmentFilePath'].append(record[1])
                    
            elif record[2] == 'inline':
                mailFields['inlineFileName'].append(record[0])
                mailFields['inlineFileMd5'].append(record[3])
                mailFields['inlineFilePath'].append(record[1])
            
        tempDb.execute(tempsensors)   
        record = tempDb.fetchone()
        mailFields['sensorID'] = record[0]
        
        tempDb.execute(tempspam)
        record = tempDb.fetchone()
        
        mailFields['firstSeen'] = str(record[0])
        mailFields['date'] = str(record[0]).split(' ')[0]
        mailFields['relayCounter'] = record[1]
        mailFields['relayTime'] = str(record[2])
        mailFields['sourceIP'] = record[3]
        mailFields['count'] = record[4]
        mailFields['to'] = record[5]
        
        
    except mdb.Error, e:
        print e
        if notify is True:
            shivanotifyerrors.notifydeveloper("[-] Error (Module shivamaindb.py) - executing temprecords %s" % e)
        
    # Checking for date.
    date = 0                                                                                                                   
    checkDate = "SELECT sdate.date FROM sdate JOIN sdate_spam ON (sdate.id = sdate_spam.date_id) WHERE sdate_spam.spam_id = '" + str(mainid) + "' AND sdate.date = '" + str(mailFields['date']) + "'"

    try:
        mainDb.execute(checkDate)
        if len(mainDb.fetchall()) >= 1:
            date = 1
    except mdb.Error, e:
        print e
        if notify is True:
            shivanotifyerrors.notifydeveloper("[-] Error (Module shivamaindb.py) - executing checkDate %s" % e)   

    if date == 0:
        insert_sdate = "INSERT INTO sdate (`date`, `firstSeen`, `lastSeen`, `todaysCounter`) VALUES('" + str(mailFields['date']) + "', '" + str(mailFields['firstSeen']) + "', '" + str(mailFields['firstSeen']) + "', '" + str(mailFields['count']) + "')"
        
        try:
            mainDb.execute(insert_sdate)
        except mdb.Error, e:
            print e
            if notify is True:
                shivanotifyerrors.notifydeveloper("[-] Error (Module shivamaindb.py) - insert_sdate %s" % e)
        
        insert_sdate_spam = "INSERT INTO sdate_spam (`spam_id`, `date_id`) VALUES('" + str(mainid) + "', '" + str(mainDb.lastrowid) + "')"
        try:
            mainDb.execute(insert_sdate_spam)
        except mdb.Error, e:
            print e
            if notify is True:
                shivanotifyerrors.notifydeveloper("[-] Error (Module shivamaindb.py) - insert_sdate_spam %s" % e)

    else:
        update_date = "UPDATE sdate JOIN sdate_spam ON (sdate.id = sdate_spam.date_id) SET sdate.lastSeen = '" + str(mailFields['firstSeen'])+"', sdate.todaysCounter = sdate.todaysCounter + '" + str(mailFields['count']) + "' WHERE sdate_spam.spam_id = '" + str(mainid) + "' AND sdate.date = '" + str(mailFields['date'])+"'"

        try:
            mainDb.execute(update_date)
        except mdb.Error, e:
            print e
            if notify is True:
                shivanotifyerrors.notifydeveloper("[-] Error (Module shivamaindb.py) - update_date %s" % e)
    
    
       
    # Checking for Recipients
    #recipients = str(mailFields['to']).split(", ")
    recipients = (mailFields['to'].encode('utf-8')).split(",")
    
    checkrecipientdb = "SELECT spam.to FROM spam WHERE spam.id = '" + str(mainid) + "'"
    mainDb.execute(checkrecipientdb)
    record = mainDb.fetchone()
    
    if record != None:
        print "inside comparing lists: "
        recipientsdb = (record[0].encode('utf-8')).split(",")
        newrecipients = [item for item in recipients if item not in recipientsdb]
        if newrecipients != '':
            newrecipients = ''.join(newrecipients)
    else:
        print "no data for it in db"
        newrecipients = mailFields['to']
    
    print "initial recipients: %s, type: %s" % (recipients, type(recipients))
    print "recipientsdb: %s, type: %s" % (recipientsdb, type(recipientsdb))    
    print "newrecipients: ", newrecipients
    print "type: ", type(newrecipients)
    print "mailFields[to]: ", mailFields['to']
    print "tyoe of mailfiled value: ", type(mailFields['to'])
    
    
    # spam table - update recipients and totalCounter
    if newrecipients == '':
        update_spam = "UPDATE `spam` SET spam.totalCounter = spam.totalCounter + '" + str(mailFields['count']) + "' WHERE spam.id = '" + str(mainid) + "'"
    else:
        update_spam = "UPDATE `spam` SET spam.totalCounter = spam.totalCounter + '" + str(mailFields['count']) + "', spam.to = CONCAT(spam.to, ',', '" + str(newrecipients) + "') WHERE spam.id = '" + str(mainid) + "'"
    
    try:
        mainDb.execute(update_spam)
    except mdb.Error, e:
        print e
        if notify is True:
            shivanotifyerrors.notifydeveloper("[-] Error (Module shivamaindb.py) - update_spam %s" % e)
    
    # Checking for IPs
    ip_list = str(mailFields['sourceIP']).split(", ")
    for ip in ip_list:            
        ipStatus = 1
        checkIP = "SELECT ip.sourceIP FROM ip JOIN ip_spam ON (ip.id = ip_spam.ip_id) WHERE ip_spam.spam_id = '" + str(mainid) + "' AND ip.sourceIP = '" + str(ip) + "'"

        try:
            mainDb.execute(checkIP)
            if len(mainDb.fetchall()) >= 1:
                ipStatus = 1
        except mdb.Error, e:
            print e
            if notify is True:
                shivanotifyerrors.notifydeveloper("[-] Error (Module shivamaindb.py) - checkIP %s" % e)

        if ipStatus == 0:
            insert_ip = "INSERT INTO ip (`date`, `sourceIP`) VALUES('" + str(mailFields['date']) + "', '" + str(ip) + "' )"
            try:
                mainDb.execute(insert_ip)
            except mdb.Error, e:
                print e
                if notify is True:
                    shivanotifyerrors.notifydeveloper("[-] Error (Module shivamaindb.py) - insert_ip %s" % e)

            insert_ip_spam = "INSERT INTO ip_spam (`spam_id`, `ip_id`) VALUES('" + str(mainid) + "', '"+str(mainDb.lastrowid)+"')"

            try:
                mainDb.execute(insert_ip_spam)
            except mdb.Error, e:
                print e
                if notify is True:
                    shivanotifyerrors.notifydeveloper("[-] Error (Module shivamaindb.py) - insert_ip_spam %s" % e)   
    
                  
            
    # Checking for Sensor ID
    sensor_list = str(mailFields['sensorID']).split(", ")
    for sensor in sensor_list:            
        sensorStatus = 1   
        checkSensorID = "SELECT sensor.sensorID FROM sensor JOIN sensor_spam ON (sensor.id = sensor_spam.sensor_id) WHERE .sensor_spam.spam_id = '" + str(mainid) + "' AND sensor.sensorID = '" + str(sensor) + "'"
        
        try:
           mainDb.execute(checkSensorID)
           if len(mainDb.fetchall()) >= 1:
                sensorStatus = 0
        except mdb.Error, e:
            print e
            if notify is True:
                shivanotifyerrors.notifydeveloper("[-] Error (Module shivamaindb.py) - checkSensorID %s" % e)

        if sensorStatus == 1:
            insert_id = "INSERT INTO sensor (`date`, `sensorID`) VALUES('"+str(mailFields['date'])+"', '"+str(sensor)+"' )"
            try:
                mainDb.execute(insert_id)
            except mdb.Error, e:
                print e
                if notify is True:
                    shivanotifyerrors.notifydeveloper("[-] Error (Module shivamaindb.py) - insert_id %s" % e)

            insert_id_spam = "INSERT INTO sensor_spam (`spam_id`, `sensor_id`) VALUES('" + str(mainid) + "', '" + str(mainDb.lastrowid)+"')"

            try:
                mainDb.execute(insert_id_spam)
            except mdb.Error, e:
                print e
                if notify is True:
                    shivanotifyerrors.notifydeveloper("[-] Error (Module shivamaindb.py) - insert_id_spam %s" % e)

  
    # Checking for URLs
    for url in mailFields['links']:
        urlstatus = 1
        checkURL = "SELECT `hyperLink` FROM `links` WHERE `spam_id` = '" + str(mainid) + "' AND `hyperLink` = '" + str(url) + "'"
        try:
            mainDb.execute(checkURL)
            records = mainDb.fetchall()
        except mdb.Error, e:
            print e
            if notify is True:
                shivanotifyerrors.notifydeveloper("[-] Error (Module shivamaindb.py) - checkURL %s" % e)
            
        if len(records) >= 1:
            urlstatus = 0
        
        if urlstatus == 1:
            insert_url = "INSERT INTO `links`(`date`, `hyperLink`, `spam_id`) VALUES ('" + str(mailFields['date']) + "', '" + str(url) + "', '" + str(mainid) + "')"
            try:
                mainDb.execute(insert_url)
            except mdb.Error, e:
                print e
                if notify is True:
                    shivanotifyerrors.notifydeveloper("[-] Error (Module shivamaindb.py) - insert_url %s" % e)

    # Checking fo attachments
    if len(mailFields['attachmentFileMd5']) != 0:
        i = 0
        while i < len(mailFields['attachmentFileMd5']):
            md5Status = 1
            checkMd5 = "SELECT `md5` FROM `attachment` WHERE `spam_id` = '" + str(mainid) + "' AND `md5` = '" + str(mailFields['attachmentFileMd5'][i]) + "'"
            try:
                mainDb.execute(checkMd5)
                records = mainDb.fetchall()
            except mdb.Error, e:
                print e
                if notify is True:
                    shivanotifyerrors.notifydeveloper("[-] Error (Module shivamaindb.py) - checkMd5 %s" % e)
            
            if len(records) >= 1:
                md5Status = 0
                
            if md5Status == 1:
                insert_attachment = "INSERT INTO `attachment`(`date`, `md5`, `attachment_file_name`, `attachment_file_path`, `attachment_file_type`, `spam_id`) VALUES('" + str(mailFields['date']) + "', '" + str(mailFields['attachmentFileMd5'][i]) + "', '" + str(mdb.escape_string(mailFields['attachmentFileName'][i].encode('utf-8'))) + "', '" + str(mdb.escape_string(mailFields['attachmentFilePath'][i].encode('utf-8'))) + "', '" + str(os.path.splitext(mailFields['attachmentFileName'][i])[1].encode('utf-8')) + "', '" + str(mainid) + "')"
                
                try:
                    mainDb.execute(insert_attachment)
                except mdb.Error, e:
                    print e
                    if notify is True:
                        shivanotifyerrors.notifydeveloper("[-] Error (Module shivamaindb.py) - insert_attachment %s" % e)
            i = i + 1
    
    # Checking fo inline attachments
    if len(mailFields['inlineFileMd5']) >= 1:
        i = 0
        while i < len(mailFields['inlineFileMd5']):
            md5Status = 1
            checkMd5 = "SELECT `md5` FROM `inline` WHERE `spam_id` = '" + str(mainid) + "' AND `md5` = '" + str(mailFields['inlineFileMd5'][i]) + "'"
            try:
                mainDb.execute(checkMd5)
                records = mainDb.fetchall()
            except mdb.Error, e:
                print e
                if notify is True:
                    shivanotifyerrors.notifydeveloper("[-] Error (Module shivamaindb.py) - checkMd5 %s" % e)
            
            if len(records) >= 1:
                md5Status = 0
                
            if md5Status == 1:
                insert_inline = "INSERT INTO `inline`(`date`, `md5`, `inline_file_name`, `inline_file_path`, `spam_id` ) VALUES('" + str(mailFields['date']) + "', '" + str(mailFields['inlineFileMd5'][i]) + "', '" + str(mdb.escape_string(mailFields['inlineFileName'][i])) + "', '" + str(mdb.escape_string(mailFields['inlineFilePath'][i])) + "', '" + str(mainid) + "')"
                try:
                    mainDb.execute(insert_inline)
                except mdb.Error, e:
                    print e
                    if notify is True:
                        shivanotifyerrors.notifydeveloper("[-] Error (Module shivamaindb.py) - insert_inline %s" % e)
            i = i + 1
            
    # Last but not the least, updating relay table.
    if int(mailFields['relayCounter']) > 0:
        relayDate = str(mailFields['relayTime']).split(' ')[0]
        checkRelayDate = "SELECT `id` FROM `relay` WHERE `spam_id` = '" + str(mainid) + "' AND `date` = '" + str(relayDate) + "'"
        try:
            mainDb.execute(checkRelayDate)
        except mdb.Error, e:
            print e
            if notify is True:
                shivanotifyerrors.notifydeveloper("[-] Error (Module shivamaindb.py) - checkRelayDate %s" % e)
            
        if len(mainDb.fetchall()) >= 1:
            update_relay = "UPDATE `relay` SET `lastRelayed` = '" + str(mailFields['relayTime']) + "', totalRelayed = totalRelayed + '" + str(mailFields['relayCounter']) + "' WHERE `spam_id` = '" + str(mainid) + "' AND `date` = '" + str(relayDate) + "'"
            try:
                mainDb.execute(update_relay)
            except mdb.Error, e:
                print e
                if notify is True:
                    shivanotifyerrors.notifydeveloper("[-] Error (Module shivamaindb.py) - update_relay %s" % e)
            
        else:
            insert_relay = "INSERT INTO `relay`(`date`, `firstRelayed`, `lastRelayed`, `totalRelayed`, `spam_id`, `sensorID`) VALUES ('" + str(relayDate) + "', '" + str(mailFields['relayTime']) + "', '" + str(mailFields['relayTime']) + "', '" + str(mailFields['relayCounter']) + "', '" + str(mainid) + "', '" + str(mailFields['sensorID']) + "')"
            try:
                mainDb.execute(insert_relay)
            except mdb.Error, e:
                print e
                if notify is True:
                    shivanotifyerrors.notifydeveloper("[-] Error (Module shivamaindb.py) - insert_relay %s" % e)
             

if __name__ == '__main__':
    tempDb = shivadbconfig.dbconnect()
    mainDb = shivadbconfig.dbconnectmain()
    notify = server.shivaconf.getboolean('notification', 'enabled')
    time.sleep(200) # Giving time to hpfeeds module to complete the task.
    main()
