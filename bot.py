#!/usr/bin/python -tt

import re
import sys

from twisted.internet import protocol
from twisted.words.protocols import irc

class Bot(irc.IRCClient):
	def _get_password(self):
		return self.factory.password
	password = property(_get_password)

	def _get_nickname(self):
		return self.factory.nickname
	nickname = property(_get_nickname)

	def _get_channels(self):
		return self.factory.channels
	channels = property(_get_channels)

	def _forMe(self, msg):
		if re.search(r'^[[:space:]]*%s[[:space:]]*[:,]' % self.nickname, msg):
			return re.sub(r'^[[:space:]]*%s[[:space:]]*[:,][[:space:]]*', msg)
		return False

	def signedOn(self):
		for chan in self.channels:
			self.join(chan)

	def joined(self, channel):
		pass

	def userJoined(self, user, channel):
		print user
		print channel

	def privmsg(self, user, channel, msg):
		nick = user.split('!', 1)[0]
		
		if channel != self.nickname:
			msg = self._forMe(msg)
			if not msg:
				return

		matches = re.search(r'^\s*reload\s+([a-z0-9_]+)\s*$', msg)
		if matches:
			module = matches.group(1)
			if module not in sys.modules:
				self.msg(nick, 'Module %s is not loaded.' % module)
				return

			reload(sys.modules[module])

#	def action(self, user, channel, msg):
#		nick = user.split('!', 1)[0]
#		self.logger.log('* %s %s' % (nick, msg))

class BotFactory(protocol.ClientFactory):
	protocol = Bot

	def __init__(self, nickname, channels, password=None):
		self.nickname = nickname
		self.channels = channels
		self.password = password
