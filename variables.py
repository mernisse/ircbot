#!/usr/bin/python -tt
""" variables.py (c) 2013 Matthew J. Ernisse <mernisse@ub3rgeek.net>
Implement a key/value interface to the Brain of the robot.

"""

import core
import re

from botlogger import *

def privmsg(self, user, channel, msg):
	speaker = user.split('!', 1)[0]
	dst = speaker
	if channel != self.nickname:
		msg = self._forMe(msg)
		if not msg:
			return

		dst = channel

	matches = re.search(
		r'^(set|get|del)\s+([a-z0-9_-]+)(\s+(\S+)\s*)?$',
		msg, re.I)

	if not matches:
		return

	verb = matches.group(1).lower()
	key = matches.group(2).upper()
	value = matches.group(4)

	if verb == 'get':
		if not speaker in core.brain:
			self.msg(dst, 'you have no variables set.', only=True)

		try:
			value = core.brain[speaker][key]
			log('variables - %s set %s = %s' % (
				speaker, key, value))

			self.msg(dst, '%s = %s' % (key, value), only=True)

		except KeyError:
			self.msg(dst, '%s is unset for you.' % key, only=True)

		
	elif verb == 'set':
		if not speaker in core.brain:
			core.brain[speaker] = { key: value }
		else:
			core.brain[speaker][key] = value

		self.msg(dst, 'now %s = %s for you.' % (key, value), only=True)

	elif verb == 'del':
		if not speaker in core.brain or \
			not key in core.brain['speaker']:
			self.msg(dst, '%s was already unset.' % key, only=True)

		core.brain[speaker].pop(key)
		self.msg(dst, 'unset %s.' % key, only=True)

core.register_module(__name__)
