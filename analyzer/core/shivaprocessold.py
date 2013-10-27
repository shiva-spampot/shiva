import logging
import datetime

import server

def main(mailFields, matchedHash, key, msgMailRequest):
    logging.info("[+]Inside shivaprocessold Module.")


    relay_enabled = server.shivaconf.getboolean('analyzer', 'relay')
    records = server.QueueReceiver.records

    for record in records:
        if record['s_id'] == matchedHash:

            if mailFields['attachmentFileMd5']:
                i = 0
                while i < len(mailFields['attachmentFileMd5']):
                    if mailFields['attachmentFileMd5'][i] not in record['attachmentFileMd5']:
                        record['attachmentFile'].append(mailFields['attachmentFile'][i])
                        record['attachmentFileMd5'].append(mailFields['attachmentFileMd5'][i])
                        record['attachmentFileName'].append(mailFields['attachmentFileName'][i])
                    i += 1

            if mailFields['links']:
                for newLink in mailFields['links']:
                    if newLink not in record['links']:
                        record['links'].append(newLink)

            if record['inlineFileMd5'] != mailFields['inlineFileMd5']:
                i = 0
                while i < len(mailFields['inlineFileMd5']):
                    if mailFields['inlineFileMd5'][i] not in record['inlineFileMd5']:
                        record['inlineFile'].append(mailFields['inlineFile'][i])
                        record['inlineFileMd5'].append(mailFields['inlineFileMd5'][i])
                        record['inlineFileName'].append(mailFields['inlineFileName'][i])
                    i += 1

            ipList = record['sourceIP'].split(", ")
            if mailFields['sourceIP'] not in ipList:
                record['sourceIP'] = record['sourceIP'] + ", " + mailFields['sourceIP']

            sensorIDs = record['sensorID'].split(", ")
            if mailFields['sensorID'] not in sensorIDs:
                record['sensorID'] =  mailFields['sensorID'] + ", " + record['sensorID']

            record['counter'] += 1
            
            if relay_enabled is True:
                relaycounter = server.shivaconf.getint('analyzer', 'globalcounter')
                individualcounter = server.shivaconf.getint('analyzer', 'individualcounter')
                if int(server.QueueReceiver.totalRelay) < relaycounter and int(record['relayed']) < individualcounter:
                    logging.info("[+]shivaprocessold Module: Relay counter has not reached limit yet. Shall relay this.")
                    
                    # Following 3 lines does the relaying
		     queuePath = server.shivaconf.get('global', 'queuepath')
		     processMessage = server.QueueReceiver(queuePath)
		     processMessage.process_message(msgMailRequest)
                    
                    record['relayed'] += 1
                    server.QueueReceiver.totalRelay += 1
                else:
                    logging.info("[+]shivaprocessold Module: Limit reached. No relay.")
