#!/usr/bin/python -tt

import core
import random
import re
import time
import os
import paramiko
import private

from botlogger import *

EVENTS = {}

def load_calendar():
	''' fetch the calendar from iorek via sftp '''
	global EVENTS

	remote = { 
		'hostname': 'iorek.ice-nine.org',
		'location': '/usr/share/calendar/calendar.iorek',
	}

#	try:
#		username = private.IOREK_USERNAME
#		password = private.IOREK_PASSWORD
#
#		transport = paramiko.Transport((remote['hostname'], 22))
#		transport.connect(
#			username = username,
#			password = password)
#
#		sftp = paramiko.SFTPClient.from_transport(transport)
#		sftp.get(remote['location'], 'calendar.iorek')
#		sftp.close()
#		transport.close()
#	except Exception, e:
#		err('topic - failed to get calendar: %s' % str(e))
#		return

	try:
		count = 0
		fd = open('calendar.iorek')
		for line in fd:
			matches = re.search(r'^(\d+)/(\d+)\s+(.*)', line, re.I)
			if not matches:
				continue

			month = matches.group(1)
			day = matches.group(2)
			event = matches.group(3)

			mmdd = "%s-%s" % ( month, day )
			count += 1
			if not mmdd in EVENTS:
				EVENTS[mmdd] = [event]
			else:
				EVENTS[mmdd].append(event)

		fd.close()

	except Exception, e:
		err('topic - failed to parse calendar: %s' % str(e))
		return

	days = len(EVENTS.keys())
	log('topic - loaded %i events for %i days' % (count, days))

def emit_event(month, day):
	global EVENTS
	mmdd = "%s-%s" % (month, day)

	if not mmdd in EVENTS:
		return '%s\%s Nothing ever happens.' % (month, day)

	return "%s\%s %s" % (
		month,
		day,
		EVENTS[mmdd][random.randint(0, len(EVENTS[mmdd]) -1)]
	)

def periodic(self):
	for channel in self.channels:	
		self.topic(channel)

def topicUpdated(self, user, channel, topic):
	#
	# if someone else set the topic, don't override it
	#
	if not user == self.nickname and topic:
		return

	thismonth = time.strftime('%m')
	thisday = time.strftime('%d')

	if not topic:
		self.topic(channel, emit_event(thismonth, thisday))
		return

	matches = re.search(r'^(\d+)/(\d+)\s+(.*)', topic, re.I)
	if not matches:
		return

	topicmonth = matches.group(1)
	topicday = matches.group(2)

	if thismonth == topicmonth and thisday == topicday:
		return

	self.topic(channel, emit_event(thismonth, thisday))

load_calendar()
core.register_module(__name__)
