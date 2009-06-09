#!/usr/bin/python -tt
""" core.py - (c) 2009 Matthew John Ernisse <mernisse@ub3rgeek.net>
provide core functions for the bot

The MODULES list holds all the names for the plugins registered to the
bot.  Each plugin should import core and core.MODULES.append(__name__)
to ensure it is present in this list.  Failure to do so will cause the
callbacks to never get processed.

Functions:
	joined(self, channel)
	userJoined(self, user, channel)
	privmsg(self, user, channel, msg)
	action(self, user, channel, msg)

Variables:
	self - the Bot class
	user - the full userspec (nick!ident@host) of the origin user
	channel - channel the event was 'seen' in, or my nick if directed.
	msg - message text of the event (if any)

"""
from botlogger import err

MODULES = []
MODULES.append('core')

def joined(self, channel):
	pass

def userJoined(self, user, channel):
	pass

def privmsg(self, user, channel, msg):
	pass

def action(self, user, channel, msg):
	pass
