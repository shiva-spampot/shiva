#! /usr/bin/python
"""
Schedules a job to reset individual counters of relayed mails to 0. 
This would make sure each spammer finds spamPot relaying everyday.
"""
import datetime
import logging

from apscheduler.scheduler import Scheduler

import shivapushtodb
import server

def resetcounter():
    localdb = server.shivaconf.getboolean('database', 'localdb')
    hpfeeds = server.shivaconf.getboolean('hpfeeds', 'enabled')    
 
    if localdb is True:
        shivapushtodb.push()
        if hpfeeds is True:
            shivapushtodb.sendfeed()
    else:
        if hpfeeds is True:
            logging.info("[+]shivascheduler.py: Local db is disabled. Sending data to hpfeeds.")
            shivapushtodb.sendfeed()
    shivapushtodb.cleanup()

def schedule():
    sched = Scheduler()
    duration = server.shivaconf.getint('analyzer', 'schedulertime')
    sched.add_interval_job(resetcounter, minutes=duration)
    sched.start()
    logging.info("Shiva scheduler started at %s. (%d minutes interval). " % (datetime.datetime.now(), duration))
