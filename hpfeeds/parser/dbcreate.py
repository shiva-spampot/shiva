#!/usr/bin/env python
""" dbcreate.py
Creates database where all the data received from Hpfeeds will be saved.
"""

import os
import sys

HOST = ""
USER = ""
PASSWD = ""

def createdb():
    try:
        os.system("mysql -h " + HOST + " -u " + USER + " --password=" + PASSWD + " < hpfeeds-db.sql")
        print "Database created."
    except Exception, e:
        print e
        sys.exit(1)

if __name__ == '__main__':
    createdb()