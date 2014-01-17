"""This module contains the database connection parameters required by 
SHIVA for MySQL connection. This module also has the functions that might
send the error notification mail and copy the spams to "distorted" folder
that cannot be analyzed. To enable error notification, edit the 
senderrornotificationmail function.
"""

import os
import logging
import shutil
import smtplib
import ConfigParser

import MySQLdb as mdb

confpath = os.path.dirname(os.path.realpath(__file__)) + "/../../../../../shiva.conf"
shivaconf = ConfigParser.ConfigParser()
shivaconf.read(confpath)

HOST = shivaconf.get('database', 'host')
USER = shivaconf.get('database', 'user')
PASS = shivaconf.get('database', 'password')


def dbconnect():
    """ Returns MySQL cursor.
    Temporary db connection parameters.
    """
    conn = None

    try:
        conn = mdb.connect (host = HOST,
                            user = USER,
                            passwd = PASS,
                            db = "ShivaTemp",
                            charset='utf8mb4',
                            use_unicode = True)
        conn.autocommit(True)
        cursor = conn.cursor()
        return cursor

    except mdb.Error, e:
        logging.critical("[-] Error (shivadbconfig.py) - %d: %s" % (e.args[0], e.args[1]))
        
def dbconnectmain():
    """Returns MySQL cursor.
    Main db connection parameters.
    """
    conn1 = None

    try:
        conn1 = mdb.connect (host = HOST,
                            user = USER,
                            passwd = PASS,
                            db = "Shiva",
                            charset='utf8mb4',
                            use_unicode = True)
        conn1.autocommit(True)
        cursor = conn1.cursor()
        return cursor

    except mdb.Error, e:
        logging.critical("[-] Error (shivadbconfig.py) - %d: %s" % (e.args[0], e.args[1]))
