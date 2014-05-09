#!/usr/bin/python -tt
''' stock.py (c) 2014 Matthew J. Ernisse <mernisse@ub3rgeek.net>

Emit stock information from the Yahoo API.

'''

import core
import csv
import re
import urllib
import urllib2

from botlogger import *

# Name, Last Trade, Change, Change %, Market Cap
FMT = "nl1c6p2j1"
URL = "http://download.finance.yahoo.com/d/quotes.csv"

def fetch_quote(symbol):
	global FMT, URL

	args = {
		"s": symbol,
		"f" : FMT,
		"e" : ".csv"
	}

	qs = urllib.urlencode(args)
	
	req = urllib2.Request(URL + "?" + qs)
	data = urllib2.urlopen(req)
	csv_data = csv.reader(data)

	row = csv_data.next()

	return "%s: %s (%s %s Cap %s)" % (
		row[0], row[1], row[2], row[3], row[4]
	)

def privmsg(self, user, channel, msg):
	dst = user.split('!', 1)[0]
	if channel != self.nickname:
		msg = self._forMe(msg)
		if not msg:
			return

		dst = channel

	matches = re.search(
		r'^ticker:?\s+([a-z0-9_.-^]+)\s*$',
		msg,
		re.I
	)

	if not matches:
		return

	symbol = matches.group(1).lower()
	try:
		msg = fetch_quote(symbol)

	except Exception, e:
		log('stock() failed to fetch symbol %s, %s' % (
			symbol, str(e)
		))
		self.msg(dst, "Failed to fetch symbol data.")
		return

	self.msg(dst, msg, only=True)

core.register_module(__name__)
