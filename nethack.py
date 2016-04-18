#!/usr/bin/python -tt
''' nethack.py (c) 2009, 2013 Matthew J. Ernisse <mernisse@ub3rgeek.net>

Module for the IRC robot that implements similar function to the Nethack
witty sayings.

Requires pom.py (ported from OpenBSD's pom.c) for Phase of Moon detection.
'''

import core
from os import stat
from pom import pom
from random import randint
import re
from stat import ST_MTIME
from time import time

from botlogger import *

NH_FIRED = {}
FORTUNES = []
FORTUNES_TSTAMP = 0

def load_fortunes():
	global FORTUNES, FORTUNES_TSTAMP

	#
	# only reload fortunes if the file has changed since we loaded it.
	#
	tstamp = stat("nethack.nki")[ST_MTIME]
	if tstamp < FORTUNES_TSTAMP:
		return True

	try:
		fd = open("nethack.nki")
		new_fortunes = []
		for line in fd:
			line = re.sub("#.*", "", line.strip())
			if not line:
				continue
			new_fortunes.append(line)

		fd.close()
		FORTUNES = new_fortunes
		FORTUNES_TSTAMP = tstamp
	except Exception, e:
		log("Could not load nethack.nki: %s" % str(e))
		return None

	return True

def privmsg(self, user, channel, msg):
	msg = self._forMe(msg)
	if not msg:
		return False

	dst = user.split('!', 1)[0]
	if channel != self.nickname:
		dst = channel

	if pom() < 99 and pom() > 1:
		return False

	# The "Phase of the moon" is 99% - 100% or 0% - 1%;
	# let's play ball.

	global NH_FIRED
	if not dst in NH_FIRED.keys():
		NH_FIRED[dst] = 0

	if NH_FIRED[dst] > (time() - 7200):
		# We fired recently (within the last 2h), so 
		# please donut annoy the channel.
		return

	if not load_fortunes():
		self.msg(dst, "The filesystem error hits! Your nethack.nki turns to dust!--More--")
		NH_FIRED[dst] = time();

	if len(FORTUNES) > 0:
		NH_FIRED[dst] = time();
		self.msg(dst, FORTUNES[randint(0, len(FORTUNES) - 1)])

#
# preload fortunes.
#
if load_fortunes():
	log('nethack: %i fortunes loaded' % (len(FORTUNES)))

core.register_module(__name__)