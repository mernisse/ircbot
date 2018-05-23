#!/usr/bin/python -tt
""" botlogger.py - (c) 2009-2017 Matthew J. Ernisse <matt@going-flying.com>
provide a generic log interface for the robot.

This module provides log() and err() which in this iteration just calls out 
to syslog() with a default loglevel of LOG_INFO, and LOG_ERR respectively 
however any logging interface could be swapped in.

"""
import logging
import logging.handlers
import os
import sys
import syslog

SYSLOG_HOST = ('localhost', 514)
SYSLOG_FACILITY = logging.handlers.SysLogHandler.LOG_USER
logger = None

def debug(s):
	global logger
	logger.debug(s)

def err(s):
	global logger
	logger.error(s)

def logException(e):
	global logger
	logger.error("Exception: ", exc_info=e)

def log(s):
	global logger
	logger.info(s)

logger = logging.getLogger("ircbot")
logger.setLevel(logging.DEBUG)

consoleHandler = logging.StreamHandler()
consoleHandler.setLevel(logging.DEBUG)

syslogHandler = logging.handlers.SysLogHandler(
	address = SYSLOG_HOST,
	facility = SYSLOG_FACILITY
)
syslogHandler.setLevel(logging.INFO)

logger.addHandler(consoleHandler)
logger.addHandler(syslogHandler)
logger.info("logging initalized...")
