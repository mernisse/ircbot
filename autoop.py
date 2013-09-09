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
		err("Failed to reload config: %s" % str(e))

def check_masks(userhost):
	global MASKS
	reload_masks()
	for mask in MASKS:
		if re.search(mask, userhost):
			return True

	return False

def whoisReply(self, nick, userinfo):
	if nick == self.nickname:
		return

	userhost = "%s@%s" % (userinfo['username'], userinfo['hostname'])

	if not check_masks(userhost):
		return

	for channel in self.chatters:
		if nick in self.chatters[channel]['users']:
			self.mode(channel, True, "o", user=nick)

core.register_module(__name__)
