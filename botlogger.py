#!/usr/bin/python -tt
""" botlogger.py - (c) 2009, 2013 Matthew John Ernisse <mernisse@ub3rgeek.net>
provide a generic log interface for the robot.

This module provides log() and err() which in this iteration just calls out 
to syslog() with a default loglevel of LOG_INFO, and LOG_ERR respectively 
however any logging interface could be swapped in.

"""
import os
import sys
import syslog

def log(s):
	syslog.syslog(syslog.LOG_INFO, str(s))
	print str(s)

def err(s):
	sys.stderr.write('%s\n' % s)
	syslog.syslog(syslog.LOG_ERR, str(s))
	
syslog.openlog(os.path.basename(sys.argv[0]), syslog.LOG_PID)
log('botlogger - logging started')
