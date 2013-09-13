import os
import sys
import ConfigParser

confpath = os.path.dirname(os.path.realpath(__file__)) + "/shiva.conf"
shivaconf = ConfigParser.ConfigParser()
shivaconf.read(confpath)

HOST = shivaconf.get('database', 'host')
USER = shivaconf.get('database', 'user')
PASSWD = shivaconf.get('database', 'password')

def tempdb():
    try:
	os.system("mysql -h " + HOST + " -u " + USER + " --password=" + PASSWD + " < tempdb.sql")
	print "Temporary database created."
    except Exception, e:
        print e
	sys.exit(1)

def maindb():
    try:
	os.system("mysql -h " + HOST + " -u " + USER + " --password=" + PASSWD + " < maindb.sql")
	print "Main database created."
    except Exception, e:
	print e
	sys.exit(1)

if __name__ == '__main__':
    tempdb()
    maindb()
