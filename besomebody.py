#!/usr/bin/python -tt
''' besomebody.py (c) 2013 Matthew J. Ernisse <mernisse@ub3rgeek.net>

Impersonate a variety of folks.

'''

import core
import random
import re
import urllib2

from bs4 import BeautifulSoup
from botlogger import *
from unidecode import unidecode

ARCHER_QUOTES = []

def archer():
	''' ...call Kenny Loggins... 'cuz you're in the Danger Zone. '''
	global ARCHER_QUOTES
	return ARCHER_QUOTES[random.randint(0, len(ARCHER_QUOTES) -1)]

def bhanat():
	''' /me pours a little out for his homies who are not here. '''
	ticketnum = random.randint(10000, 999999)
	return "<postit>%s</postit>" % str(ticketnum)

def quote_from_disk(who, index=None):
	''' emit a quote from nicks/who.txt '''
	sayings = []
	try:
		fd = open("nick/%s.txt" % (who))
		for line in fd:
			line = line.strip()
			
			if not line:
				continue

			sayings.append(line)
	except Exception, e:
		err('besomebody - failed to load quotes %s' % str(e))
		return "I do not know of whom you speak."

	if not index:
		index = random.randint(1, len(sayings) - 1)

	return sayings[index]

def load_archer_quotes():
	global ARCHER_QUOTES
	url = 'http://en.wikiquote.org/wiki/Archer_(TV_series)'
	try:
		request = urllib2.Request(url)
		request.add_header('User-Agent', 'ircbot/1.0 (python)')
		page = urllib2.urlopen(request)
	except Exception, e:
		err('archer.load_quotes() failed: %s' % str(e))
		return

	parsed = BeautifulSoup(page)
	if not parsed:
		err('archer.load_quotes() failed to parse html')
		return

	quotes = parsed.findAll('dl')
	for quote in quotes:
		ARCHER_QUOTES.append(quote.get_text())

	log('archer loaded %i quotes' % len(ARCHER_QUOTES))

def privmsg(self, user, channel, msg):
	dst = user.split('!', 1)[0]
	if channel != self.nickname:
		msg = self._forMe(msg)
		if not msg:
			return

		dst = channel

	matches = re.search(
		r'^be\s+([a-z0-9_.-]+)(?:\[(\d+)\])?\s*$',
		msg,
		re.I
	)

	if not matches:
		return

	who = matches.group(1).lower()

	if not re.search(r'^[a-z0-9_.-]+$', who):
		return "Nope, not gonna do it."

	if who == "bhanat":
		self.msg(dst, bhanat(), only=True)

	elif who == "archer":
		self.msg(dst, archer(), only=True)

	else:
		index = matches.group(2)
		self.msg(dst, quote_from_disk(who, index), only=True)
	

load_archer_quotes()
core.register_module(__name__)
