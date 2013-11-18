"""This module inserts spam's details into a temporary list. This gets called 
everytime our analyzer come across a new/distinct spam. First, all the parser 
fields are stored as a dictionary and then, that dictionary is appended into
the list. 
"""

import logging
import server
import shutil
import datetime

import server

def main(mailFields, key, msgMailRequest):
    """Main function. 
    Stores the parsed fields as dictionary and then appends it to our
    temporary list.
    """
    logging.info("Inside shivaaddnewrecord Module.")

    rawspampath = server.shivaconf.get('analyzer', 'rawspampath')
    queuepath = server.shivaconf.get('global', 'queuepath')    
    relay_enabled = server.shivaconf.getboolean('analyzer', 'relay')
    
    records = server.QueueReceiver.records
    source = queuepath + "/new/" + key
    filename = mailFields['s_id'] + "-" + key
    destination = rawspampath + filename
    shutil.copy2(source, destination) # shutil.copy2() copies the meta-data too

    newRecord = { 'headers':mailFields['headers'], 
                'to':mailFields['to'], 
                'from':mailFields['from'], 
                'subject':mailFields['subject'], 
                'date':mailFields['date'], 
                'firstSeen':mailFields['firstSeen'], 
                'lastSeen':mailFields['lastSeen'], 
                'firstRelayed':mailFields['firstRelayed'], 
                'lastRelayed':mailFields['lastRelayed'], 
                'sourceIP':mailFields['sourceIP'], 
                'sensorID':mailFields['sensorID'], 
                'text':mailFields['text'], 
                'html':mailFields['html'], 
                'inlineFileName':mailFields['inlineFileName'], 
                'inlineFile':mailFields['inlineFile'], 
                'inlineFileMd5':mailFields['inlineFileMd5'], 
                'attachmentFileName': mailFields['attachmentFileName'],
                'attachmentFile':mailFields['attachmentFile'], 
                'attachmentFileMd5':mailFields['attachmentFileMd5'], 
                'links':mailFields['links'], 
                'ssdeep':mailFields['ssdeep'], 
                's_id':mailFields['s_id'], 
                'len':mailFields['len'], 
                'counter':1, 
                'relayed':0 }

    if relay_enabled is True:
        relaycounter = server.shivaconf.getint('analyzer', 'globalcounter')

        if (int(server.QueueReceiver.totalRelay) < relaycounter) | (mailFields['to'] in server.spammers_email):
            logging.info("[+]shivaaddnewrecord Module: Relay counter has not reached limit yet. Shall relay this.")
            
	    # Following 3 lines does the relaying
	    queuePath = server.shivaconf.get('global', 'queuepath')
	    processMessage = server.QueueReceiver(queuePath)
	    processMessage.process_message(msgMailRequest)

            newRecord['relayed'] += 1
            server.QueueReceiver.totalRelay += 1
        else:
           logging.info("[+]shivaaddnewrecord Module: Limit reached. No relay.")
            
    records.insert(0, newRecord) #Inserting new record at the first position.
    del newRecord
