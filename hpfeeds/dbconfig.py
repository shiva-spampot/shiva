import MySQLdb as mdb
import os
import ConfigParser

confpath = os.path.dirname(os.path.realpath(__file__)) + "/../../../../../../shiva.conf"
shivaconf = ConfigParser.ConfigParser()
shivaconf.read(confpath)

HOST = shivaconf.get('database', 'host')
USER = shivaconf.get('database', 'user')
PASS = shivaconf.get('database', 'password')

def dbconnect():
    """
    DB connectionn parameters
    """
    conn = None

    try:
        conn = mdb.connect (host = HOST,
                            user = USER,
                            passwd = PASS,
                            db = "Temp",
                            charset='utf8',
                            use_unicode = True)
        conn.autocommit(True)
        cursor = conn.cursor()
        return cursor

    except mdb.Error, e:
        print "[-]dbconfig: Error connecting to database in hpfeeds. %s" % e
        sys.exit(1)