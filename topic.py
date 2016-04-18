#!/usr/bin/python -tt
''' topic.py (c) 2013 Matthew J Ernisse <mernisse@ub3rgeek.net>

Take a custom BSD-style calendar(1) file and set a topic on all joined 
channels from the notable events of the day.

This tries to be polite, if the topic doesn't look like an event it won't 
change the topic.

'''
import core
import feedparser
import random
import re
import time
import os

from botlogger import *

EVENTS = {}

def load_alternate_rss(url):
	''' Load an alternate source from an RSS feed '''

	try:
		parsed = feedparser.parse(url)
		topic = parsed['entries'][0].get('title', None)
		if not topic:
			return

		return topic

	except Exception, e:
		err('topic - failed to parse rss data from %s: %s' % (
			url, str(e)))
		return

def load_calendar():
	''' load a bsd style calendar(1) file '''
	global EVENTS

	try:
		fd = open('calendar')
		for line in fd:
			matches = re.search(r'^(\d+)/(\d+)\s+(.*)', line, re.I)
			if not matches:
				continue

			month = matches.group(1)
			day = matches.group(2)
			event = matches.group(3)

			mmdd = "%s-%s" % ( month, day )

			if not mmdd in EVENTS:
				EVENTS[mmdd] = [event]
			else:
				EVENTS[mmdd].append(str(event))

		fd.close()

	except Exception, e:
		err('topic - failed to parse calendar: %s' % str(e))
		return

	log('topic loaded events.')
	
def emit_event(month, day):
	''' return an event string, if nothing is in the calendar file for
	today, emit a default string.

	'''
	global EVENTS
	mmdd = "%s-%s" % (month, day)

	if not mmdd in EVENTS:
		url = "http://www.history.com/this-day-in-history/rss"
		event = load_alternate_rss(url)
		if not event:
			return '%s/%s Nothing ever happens.' % (
				month, day
			)

		return '%s/%s %s' % (month, day, event) 

	return "%s/%s %s" % (
		month,
		day,
		EVENTS[mmdd][random.randint(0, len(EVENTS[mmdd]) -1)]
	)

def topicUpdated(self, user, channel, topic):
	''' topicUpdated() gets called by the default irc_RPL_TOPIC()
	so catch that.

	Be polite.

	'''
	thismonth = time.strftime('%m')
	thisday = time.strftime('%d')
	event = emit_event(thismonth, thisday)

	if not topic:
		# if the topic is unset, that's a signal we can take it over.
		# this is what happens if the channel is new / never had a topic
	 	# (the user will be set to the server name).
		self.topic(channel, event)
		return

	matches = re.search(r'^(\d+)[/\\](\d+)\s+(.*)', topic, re.I)
	if not matches:
		return

	topicmonth = matches.group(1)
	topicday = matches.group(2)

	if thismonth == topicmonth and thisday == topicday:
		return

	self.topic(channel, event)

def periodic(self):
	''' get all the topics for all the channels we are joined to. '''
	for channel in self.chatters:
		self.topic(channel)

load_calendar()
core.register_module(__name__)
