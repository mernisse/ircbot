#!/usr/bin/python -tt

import re
import sys

from twisted.internet import protocol, reactor
from twisted.internet.ssl import ClientContextFactory
from twisted.words.protocols import irc

import config
from botlogger import *
from core import MODULES

# bot modules
import core
import testmod

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
		log('Joined channel %s' % channel)
		for mod in MODULES:
			if getattr(sys.modules[mod], 'joined', None):
				sys.modules[mod].joined(self, channel)

	def userJoined(self, user, channel):
		log('User %s joined channel %s.' % (user, channel))
		for mod in MODULES:
			if getattr(sys.modules[mod], 'userJoined', None):
				sys.modules[mod].userJoined(self, user, channel)

	def privmsg(self, user, channel, msg):
		nick = user.split('!', 1)[0]

		err('MSG: %s %s %s' % (nick, channel, msg))
		for mod in MODULES:
			if getattr(sys.modules[mod], 'privmsg', None):
				sys.modules[mod].privmsg(self, user, channel, msg)
		
		if channel != self.nickname:
			msg = self._forMe(msg)
			if not msg:
				return

		matches = re.search(r'^\s*reload\s+([a-z0-9_]+)\s*$', msg)
		if matches:
			if not nick in config.owners:
				err('%s tried to reload %s, not an owner' % (
					nick,
					module
				))
				return

			module = matches.group(1)
			if module not in sys.modules:
				self.msg(nick, 'Module %s is not loaded.' % module)
				return

			log('Reloading module %s at request of %s' % (
				module,
				nick
			))
			reload(sys.modules[module])

	def action(self, user, channel, msg):
		nick = user.split('!', 1)[0]
		err('ACTION %s %s %s' % (nick, channel, msg))
		for mod in MODULES:
			if getattr(sys.modules[mod], 'action', None):
				sys.modules[mod].action(self, user, channel, msg)

class BotFactory(protocol.ClientFactory):
	protocol = Bot

	def __init__(self, nickname, channels, password=None):
		self.nickname = nickname
		self.channels = channels
		self.password = password

if __name__ == '__main__':
	if config.ssl:
		log('Connecting to %s:%i with SSL' % (config.host, config.port))
		reactor.connectSSL(config.host, config.port,
			BotFactory(config.nickname, config.channels, config.password),
			ClientContextFactory())
	else:
		log('Connecting to %s:%i' % (config.host, config.port))
		reactor.connectTCP(config.host, config.port,
			BotFactory(config.nickname, config.channels, config.password))
	reactor.run()
