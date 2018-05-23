''' topic.py (c) 2013 - 2018 Matthew J Ernisse <matt@going-flying.com>

Take a custom BSD-style calendar(1) file and set a topic on all joined 
channels from the notable events of the day.

This tries to be polite, if the topic doesn't look like an event it won't 
change the topic.

Redistribution and use in source and binary forms,
with or without modification, are permitted provided
that the following conditions are met:

    * Redistributions of source code must retain the
      above copyright notice, this list of conditions
      and the following disclaimer.
    * Redistributions in binary form must reproduce
      the above copyright notice, this list of conditions
      and the following disclaimer in the documentation
      and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS
OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR
TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE
USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
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

	except Exception as e:
		logException(e)
		return

def load_all_calendars():
	""" Load all calendar files from a directory. """
	global EVENTS

	calPath = core.config.getChildren("topic").getStr("path")
	if not os.path.exists(calPath):
		return

	for fn in os.listdir(calPath):
		if not fn.startswith("calendar"):
			continue

		load_calendar(os.path.join(calPath, fn))

	log('topic - loaded {} events.'.format(len(EVENTS)))

def load_calendar(fn):
	''' load a bsd style calendar(1) file '''
	global EVENTS

	try:
		with open(fn) as fd:
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
					EVENTS[mmdd].append(event)

	except Exception as e:
		logException(e)
		return

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

load_all_calendars()
core.register_module(__name__)
