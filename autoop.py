#!/usr/bin/python -tt
''' autoop.py

Automatically try to +o people who join the channel with a matching usermask

'''

import core
import os
import re
import time

from botlogger import *
from stat import ST_MTIME

CONFIG = 'autoop.conf'
MASKS = []
MASKS_TSTAMP = 0

def reload_masks():
	''' reload the configuration from disk '''

	global CONFIG, MASKS, MASKS_TSTAMP
	if not os.path.exists(CONFIG):
		return

	masks_tstamp = os.stat(CONFIG)[ST_MTIME]
	if masks_tstamp < MASKS_TSTAMP:
		return

	try:
		fd = open(CONFIG)
		new_masks = []
		for line in fd:
			line = re.sub("#.*", "", line.strip())
			if not line:
				continue

			new_masks.append(line)
		fd.close()
		MASKS = new_masks
		MASKS_TSTAMP = masks_tstamp
	except Exception, e:
		log("Failed to reload config: %s" % str(e))

def check_masks(userhost):
	global MASKS
	reload_masks()
	for mask in MASKS:
		if re.search(mask, userhost):
			return True

	return False

def userJoined(self, user, channel):
	self.whois(user)

def joined(self, channel):
	# when we join a channel look around for people to op.
	self.names(channel)

def namesReply(self, channel, nicklist):
	for nick in nicklist:
		self.whois(nick)

def whoisReply(self, nick, userinfo):
	userhost = "%s@%s" % (userinfo['username'], userinfo['hostname'])
	if not check_masks(userhost):
		return

	for channel in self.channels:
		self.mode(channel, True, "o", user=nick)

def modeChanged(self, user, channel, set, modes, args):
	if not channel.startswith("#"):
		# if the channel doesn't start with a hash then it is a user
		# mode change or a server mode change not a channel mode change.
		return

	self.names(channel)

core.register_module(__name__)
