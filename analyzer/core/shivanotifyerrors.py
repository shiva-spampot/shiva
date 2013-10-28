'''
  __author__ = b0nd
  ver 1.0, 27th Oct, 2013
  
  Module sends notifications to developer/maintainer
  
'''
import shutil
import os
import smtplib
import ConfigParser
import server

confpath = os.path.dirname(os.path.realpath(__file__)) + "/../../../../../shiva.conf"
shivaconf = ConfigParser.ConfigParser()
shivaconf.read(confpath)

senderid = shivaconf.get('notification', 'sender')
recipient = shivaconf.get('notification', 'recipient')
smtphost = shivaconf.get('analyzer', 'relayhost')
smtpport = shivaconf.get('analyzer', 'relayport')



## Error notification in case script confronts any issue
def notifydeveloper(msg):
  message = """From: SHIVA spamp0t <my.spamp0t@somedomain.com>
To: Developer <developer@somedomain.com>
MIME-Version: 1.0
Content-type: text/html
Subject: Master, SHIVA spamp0t confronted an issue
"""
  message += "Error Message:\n%s" % msg
  message += "you shall find sample in distorted directory"
  
  try:
    smtpobj = smtplib.SMTP(smtphost, smtpport)
    smtpobj.sendmail(senderid, recipient, message)
    print "\n\t[+] Error Notification Mail Sent Successfully"
  except smtplib.SMTPException:
    print "\n\t[!] Error: unable to send error notification mail via Exim4"
