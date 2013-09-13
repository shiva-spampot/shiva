"""This module decides that whether a spam is new or old. It checks this by 
comparing the old spam against the records, we already have in our temporary
list. It first compares Md5 checksum, if not found, it compares against the
SSDEEP hash. If spam is new, it passes it to shivaaddnewrecord module,
for further processing. If it's an old spam, it passes it to shivaprocessold
module.
"""

import logging

import server
import ssdeep

import shivaaddnewrecord
import shivaprocessold


def main(mailFields, key, msgMailRequest):
    """Decides if a spam is new or old.
    Takes following parameters:
    a. mailFields - parsed spam fields,
    b. key - spam file name,
    c. msgMailRequest - original spam that is to be relayed.
    
    Passes spam to shivaaddnewrecord module if spam is new or list is empty.
    Else, passes spam to shivaprocessold module.
    """
    logging.info("[+]Inside shivadecide module.")
    records = server.QueueReceiver.records

    # Checking if we have any item in our global list.
    # If no item: then we will directly push spam details into the list
    # Else: Do the processing.

    if not records:
        shivaaddnewrecord.main(mailFields, key, msgMailRequest)

    else:
        if mailFields['text']:
            threshold = 75
        else:
            threshold = 85

        oriLen   = int(mailFields['len'])
        minLen, maxLen = int(oriLen * 0.90), int(oriLen * 1.10)

        count = 0
        for record in records:

            if record['len'] >= minLen and record['len'] <= maxLen:

                if mailFields['s_id'] is record['s_id']:
                    shivaprocessold.main(mailFields, record['s_id'], key, msgMailRequest)

                else:
                    ratio = ssdeep.compare(mailFields['ssdeep'], record['ssdeep'])

                    if ratio >= threshold:
                        shivaprocessold.main(mailFields, record['s_id'], key, msgMailRequest)
                        break

            count += 1

        if count == len(records):
            shivaaddnewrecord.main(mailFields, key, msgMailRequest)
