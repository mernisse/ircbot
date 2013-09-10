#!/usr/bin/python -tt

import core
import os
import re

from botlogger import *

def privmsg(self, user, channel, msg):
	dst = user.split('!', 1)[0]
	if channel != self.nickname:
		msg = self._forMe(msg)
		if not msg:
			return None

		dst = channel

	matches = re.search(r'^ascii\s+([a-z0-9_.-]+)\s*$', msg, re.IGNORECASE)
	if not matches:
		return 

	what = matches.group(1).lower()

	if what == 'list':
		try:
			available = []
			files = os.listdir('ascii/')
			for f in files:
				if not f.endswith('.txt'):
					continue
				fn, ext = os.path.splitext(os.path.basename(f))
				available.append(fn)
		
		except Exception, e:
			err('ascii - problem listing options: %s' % str(e))
			self.msg(dst, "It's a secret.")

		self.msg(dst, ' '.join(available), only=True)

	art = ascii(what)
	if not art:
		raise core.StopCallBacks

	if type(art) == str:
		self.msg(dst, art)
		raise core.StopCallBacks

	for line in art:
		if line == '\n':
			line = ' '
		self.msg(dst, line)

	raise core.StopCallBacks

def ascii(what):
	# The utterance regex above only matches these characters, but
	# we'll double-check, Just In Case.
	if not re.search(r'^[a-z0-9_.-]+$', what):
		return "Nope, not gonna do it."

	try:
		fd = open("ascii/%s.txt" % (what))
	except:
		return "I do not know of what you speak."

	art = fd.readlines()
	fd.close()
	return art

core.register_module(__name__)
