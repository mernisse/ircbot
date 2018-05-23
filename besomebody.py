''' besomebody.py (c) 2013 - 2018 Matthew J. Ernisse <matt@going-flying.com>

Impersonate a variety of folks.

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

TODO:
	preload quotes from disk into memory and watch for changes.

'''

import core
import random
import re
import requests

from bs4 import BeautifulSoup
from botlogger import *

ARCHER_QUOTES = []

def archer():
	''' ...call Kenny Loggins... 'cuz you're in the Danger Zone. '''
	global ARCHER_QUOTES
	return ARCHER_QUOTES[random.randint(0, len(ARCHER_QUOTES) -1)]

def afraid():
	'''I am not the Kwisatz Haderach...'''
	litany = ['I must not fear.',
		'Fear is the mind-killer.',
		'Fear is the little-death that brings total obliteration.',
		'I will face my fear.',
		'I will permit it to pass over me and through me.',
		'And when it has gone past I will turn the inner eye to see its path.',
		'Where the fear has gone there will be nothing.',
		'Only I will remain.',
	]
	return '\n'.join(litany)

def bhanat():
	''' /me pours a little out for his homies who are not here. '''
	ticketnum = random.randint(10000, 999999)
	return "<postit>%s</postit>" % str(ticketnum)

def quote_from_disk(who, index=None):
	''' emit a quote from nicks/who.txt '''
	sayings = []
	try:
		with open("nick/%s.txt" % (who)) as fd:
			line = fd.readline()
			if line:
				sayings.append(line)

	except Exception as e:
		err('besomebody - failed to load quotes %s' % str(e))
		return "I do not know of whom you speak."

	if not index:
		index = random.randint(0, len(sayings) - 1)

	return sayings[index]

def load_archer_quotes():
	global ARCHER_QUOTES
	url = 'http://en.wikiquote.org/wiki/Archer_(TV_series)'
	try:
		response = requests.get(url, headers={
			'User-Agent': 'ircbot/1.0 (python)'
		})
		response.raise_for_status()
		page = response.text
	except Exception as e:
		err('archer.load_quotes() failed: %s' % str(e))
		return

	parsed = BeautifulSoup(page, "lxml")
	if not parsed:
		err('archer.load_quotes() failed to parse html')
		return

	quotes = parsed.findAll('dl')
	if not quotes:
		err('archer.load_quotes(): failed to find quotes in html')
		return

	for quote in quotes:
		ARCHER_QUOTES.append(quote.text.encode('ascii', 'ignore'))

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

	elif who == "afraid":
		self.msg(dst, afraid(), only=True)

	else:
		index = matches.group(2)
		self.msg(dst, quote_from_disk(who, index), only=True)
	

load_archer_quotes()
core.register_module(__name__)
