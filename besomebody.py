#!/usr/bin/python -tt

import core
from random import randint
import re

from botlogger import *

def privmsg(self, user, channel, msg):
	dst = user.split('!', 1)[0]
	if channel != self.nickname:
		msg = self._forMe(msg)
		if not msg:
			return

		dst = channel

	message = besomebody(msg)
	if not message:
		return None

	self.msg(dst, message, only=True)

def besomebody(msg):
	matches = re.search(r'^be\s+([a-z0-9_.-]+)(?:\[(\d+)\])?\s*$', msg, re.IGNORECASE)
	if not matches:
		return

	who = matches.group(1).lower()

	if not re.search(r'^[a-z0-9_.-]+$', who):
		return "Nope, not gonna do it."

	if who == "bhanat":
		return "<postit>" + str(randint(1, 9)) + str(randint(1, 9)) + \
		str(randint(1, 9)) + str(randint(1, 9)) + str(randint(1, 9)) + \
		"</postit>"

	sayings = []
	try:
		fd = open("nick/%s.txt" % (who))
		for line in fd:
			line = line.strip()
			sayings.append(line)
	except:
		return "I do not know of whom you speak."

	if matches.groups()[1]:
		index = int(matches.group(2))
	else:
		index = randint(1, len(sayings))

	if index > len(sayings) or index < 1:
		return "Nope, not gonna do it."

	index -= 1
	return sayings[index]

core.register_module(__name__)
