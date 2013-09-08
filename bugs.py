#!/usr/bin/python -tt

import btsutils.debbugs
import core
import re

from botlogger import *

def debbugs_summary(nr):
	try:
		bts = btsutils.debbugs.debbugs()
		bug = bts.get(int(nr))
	except Exception, e:
		log('debbugs error: %s' % str(e))
		return "Couldn't fetch debbugs bug %i: %s" % (int(nr), str(e))

	return 'DB: %i - %s by %s, at %s' % (
		int(nr), bug.summary, bug.submitter, bug.url
	)

def privmsg(self, user, channel, msg):
	dst = user.split('!', 1)[0]
	if channel != self.nickname:
		dst = channel

	matches = re.search(r'(?:^|\W)debbugs?\s*(\d+)', msg, re.I)
	if not matches:
		return None

	bug = debbugs_summary(matches.group(1))

	if not bug:
		return

	self.msg(dst, bug, only=True)

core.register_module(__name__)
