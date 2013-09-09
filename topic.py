#!/usr/bin/python -tt
''' topic.py (c) 2013 Matthew J Ernisse <mernisse@ub3rgeek.net>

Take a custom calendar(1) file from a remote server and set a topic
on the channel from the notable events of the day.

This tries to be polite, if the topic is set by someone other than the bot
or if the topic doesn't look like an event it won't change the topic.

'''
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
	''' fetch the calendar from a remote server via sftp '''
	global EVENTS

	remote = { 
		'username': private.SFTP_USERNAME,
		'password': private.SFTP_PASSWORD,
		'hostname': private.SFTP_HOSTNAME,
		'location': private.SFTP_LOCATION,
	}

	try:

		transport = paramiko.Transport((remote['hostname'], 22))
		transport.connect(
			username = remote['username'],
			password = remote['password'])

		sftp = paramiko.SFTPClient.from_transport(transport)
		sftp.get(remote['location'], private.SFTP_LOCAL)
		sftp.close()
		transport.close()
	except Exception, e:
		err('topic - failed to get calendar: %s' % str(e))
		return

	try:
		count = 0
		fd = open(private.SFTP_LOCAL)
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
	''' return an event string, if nothing is in the calendar file for
	today, emit a default string.

	'''
	global EVENTS
	mmdd = "%s-%s" % (month, day)

	if not mmdd in EVENTS:
		return '%s\%s Nothing ever happens.' % (month, day)

	return "%s\%s %s" % (
		month,
		day,
		EVENTS[mmdd][random.randint(0, len(EVENTS[mmdd]) -1)]
	)

def topicUpdated(self, user, channel, topic):
	''' topicUpdated() gets called by the default irc_RPL_TOPIC()
	so catch that.

	Be polite.

	'''
	if not user == self.nickname and topic:
		return

	thismonth = time.strftime('%m')
	thisday = time.strftime('%d')

	if not topic:
		# if the topic is unset, that's a signal we can take it over.
		# this is what happens if the channel is new / never had a topic
	 	# (the user will be set to the server name).
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

def periodic(self):
	''' get all the topics for all the channels we are joined to. '''
	for channel in self.channels:	
		self.topic(channel)

load_calendar()
core.register_module(__name__)
