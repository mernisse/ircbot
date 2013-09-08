#!/usr/bin/python -tt
''' archer.py (c) 2013 Matthew J Ernisse <mernisse@ub3rgeek.net>

Emit a random Archer quote from wikiquote.org 

'''

import core
import random
import re
import urllib2

from bs4 import BeautifulSoup
from botlogger import *
from unidecode import unidecode

QUOTES = []

def load_quotes():
	global QUOTES

	url = 'http://en.wikiquote.org/wiki/Archer_(TV_series)'
	try:
		request = urllib2.Request(url)
		request.add_header('User-Agent', 'ircbot/1.0 (python)')
		page = urllib2.urlopen(request)
	except Exception, e:
		log('archer.load_quotes() failed: %s' % str(e))
		return

	parsed = BeautifulSoup(page)
	if not parsed:
		log('archer.load_quotes() failed to parse html')
		return

	quotes = parsed.findAll('dl')
	for quote in quotes:
		QUOTES.append(quote.get_text())

	log('archer loaded %i quotes' % len(QUOTES))

def privmsg(self, user, channel, msg):
	global QUOTES

	dst = user.split('!', 1)[0]
	if channel != self.nickname:
		msg = self._forMe(msg)
		if not msg:
			return

		dst = channel

	matches = re.search(r'^be\s+([a-z0-9_.-]+)(?:\[(\d+)\])?\s*$', msg, re.IGNORECASE)
	if not matches:
		return

	who = matches.group(1).lower()
	if who != 'archer':
		return

	try:
		quote = QUOTES[random.randint(0, len(QUOTES) - 1)]
		if not quote:
			log('archer - could not randomly select a quote')
			return

	except Exception, e:
		log('archer - something really naughty happened %s' % str(e))
		return

	quote = quote.split('\n')
	for line in quote:
		line = unidecode(line)
		self.msg(dst, line)

	raise core.StopCallBacks

load_quotes()
core.register_module(__name__)
