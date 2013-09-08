#!/usr/bin/python -tt
''' hateball.py (c) 2013 Matthew J. Ernisse <mernisse@ub3rgeek.net>

Module for irc bot that implements a magic hate ball-esque reply of last
resort for directed speech to the bot.

'''

import core
import random
import re
import simplejson

from botlogger import *

FATES = ''

def privmsg(self, user, channel, msg):
	global FATES

	msg = self._forMe(msg)
	if not msg:
		return

	speaker = user.split('!', 1)[0]
	dst = channel

	if not FATES:
		return

	hatred = FATES[random.randint(0, len(FATES) -1)]
	self.msg(dst, '%s: %s' % (speaker, hatred), only=True)

#
# Load fates at import
#
try:
	fd = open('fates.json')
	for line in fd:
		FATES = FATES + line.strip()

	FATES = simplejson.loads(FATES)
	log('hateball loaded %i fates' % len(FATES))

except Exception, e:
	log('hateball failed to load fates %s' % str(e))

fd.close()
core.register_module(__name__)
