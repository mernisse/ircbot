#!/usr/bin/python -tt
# coding: utf-8 
"""__init__.py - (c) 2013-2014 Matthew John Ernisse <mernisse@ub3rgeek.net>

Catch, log, and shorten urls.  Uses uber.hk because that is mine.

"""
import core
from botlogger import *

import db
import handlers
import uber

__all__ = ["db", "handlers", "uber"]

def privmsg(self, user, channel, msg):
	''' Module hook function for the ircbot.  Called on receipt of
	a privmsg.

	'''
	speaker = user.split('!', 1)[0]

	#
	# look for a url in the incoming text
	#
	urls = handlers.core.detect_valid_urls(msg)
	if not urls:
		return

	try:
		for url in urls:
			url, title = handlers.processurl(url)

			#
			# handle DB bullshit and shortening here.
			#
			row = db.fetch_url_db(url)

			if not row:
				# New URL.
				short = uber.shorten(url)
				db.add_url_to_db(url, short, speaker)
				self.msg(channel, "%s [%s]" % (short, title))
				continue

			# Not new URL
			short = row[2]
			count = row[4]
			db.update_url_in_db(short, count)
			self.msg(channel, "%s [%s, mentioned %ix]" % (
				short, title, int(count) + 1))
			continue

		raise core.StopCallBacks

	except core.StopCallBacks:
		raise

	except Exception, e:
		err('uberurls - Error: %s' % (str(e)))
		self.msg(channel, "╯(°□°)╯ ︵┻━┻  %s" % (
			str(e)), only=True)

core.register_module(__name__)
