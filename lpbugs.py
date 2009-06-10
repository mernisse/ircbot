#!/usr/bin/python -tt
"""lpbugs.py - (c) 2009 Matthew John Ernisse <mernisse@ub3rgeek.net>

Provide Launchpad integration for ircbot

Keyword(s): lp, lpbugs, launchpad, ubuntubugs

Requires: python-launchpadlib or similar.  Initial setup will be required
by running this standalone.  You will want to run (python ./lpbugs.py) this
as the user that will run the irc bot as it stores the authentication creds
in the $HOME of the user it is executed as.

"""
import core
import os
import re
import sys

from botlogger import *
from launchpadlib.credentials import Credentials
from launchpadlib.launchpad import Launchpad, EDGE_SERVICE_ROOT

CONFDIR = os.path.expanduser('~/.launchpadlib')
CACHEDIR = '%s/cache' % CONFDIR
LP = None

def privmsg(self, user, channel, msg):
	dst = user.split('!', 1)[0]
	if channel != self.nickname:
		msg = self._forMe(msg)
		if not msg:
			return

		dst = channel

	matches = re.search(r'^\s*(lp|lpbugs|launchpad|ubuntubugs):*\s+(\d+)\s*$', msg)
	if not matches:
		return

	bug_id = int(matches.group(2))
	try:
		bug = LP.bugs[bug_id]
	except Exception, e:
		self.msg(dst, 'Could not find lp bug %i, %s' % (
			bug_id,
			str(e)
		))
		return

	owner = str(bug.owner).split('~', 1)[1]
	self.msg(dst, str('LP bug #%i, %s (%s) by %s' % (
		bug_id,
		bug.title,
		bug.self_link,
		owner
	)))

# this is the module initialization process if we are imported.
if __name__ == 'lpbugs':
	creds = Credentials()
	creds.load(open('%s/lpcreds.txt' % CONFDIR))
	LP = Launchpad(creds, EDGE_SERVICE_ROOT, CACHEDIR)
	core.MODULES.append(__name__)
	log('%s Loaded Successfully' % __name__)
	
# This is the setup initialization process
if __name__ == '__main__':
	if not os.path.exists(CACHEDIR):
		print "Creating conf and cache dir"
		try:
			os.makedirs(CACHEDIR)
		except Exception, e:
			print 'Error creating directories, %s' % str(e)
			sys.exit(1)

	if os.path.exists('%s/lpcreds.txt' % CONFDIR):
		creds = Credentials()
		creds.load(open('%s/lpcreds.txt' % CONFDIR))
		LP = Launchpad(creds, EDGE_SERVICE_ROOT, CACHEDIR)
		bug = LP.bugs[1]
		print '%s (%s) By %s' % (bug.title, bug.self_link, bug.owner)
		sys.exit(0)
		
	lp = Launchpad.get_token_and_login('ircbot', EDGE_SERVICE_ROOT, CACHEDIR)
	try:
		bug_one = lp.bugs[1]
	except Exception, e:
		print str(e)
		sys.exit(1)

	lp.credentials.save(file('%s/lpcreds.txt' % CONFDIR, 'w'))
	print 'Configuration successful'
