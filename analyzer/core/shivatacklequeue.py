"""
Shiva - This module just passes informationto analyzing modules.
The variable msgMailRequest has been passed to all subsequent modules and functions. 
None of other module needs it but process_message function needs this value. 
Could not find a direct way to assign this value to process_message, hence
the same value has been circulated throughout all modules/functions and ultimately 
it reaches process_message.
"""

import server
import shivamailparser


def process_message(msgMailRequest):
    """This function gets called only when a spam has to be relayed
    """
    queuePath = server.shivaconf.get('global', 'queuepath')
    processMessage = server.QueueReceiver(queuePath)
    processMessage.process_message(msgMailRequest)


def tacklequeue(key, msgMailRequest):
    """This function gets called from QueueReceiver function of module server.py
    """
    shivamailparser.main(key, msgMailRequest)
