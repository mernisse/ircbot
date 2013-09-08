#!/usr/bin/python -tt

import re
import sys

from twisted.internet import protocol, reactor
from twisted.internet.ssl import ClientContextFactory
from twisted.words.protocols import irc

import config
from botlogger import *
from core import MODULES

# bot modules - callbacks should be registered at import so the import order
# here is also the execution order.

# core should always be first.
import core

# this should happen before everything else.
import nethack

import variables

import ascii
import archer
import besomebody
import bugs
import remotecontrol
import sms
import uberurls

# this should happen last
import hateball

class Bot(irc.IRCClient):
	def msg(self, user, message, length=None, only=None):
		''' Overload irc.IRCClient.msg() so that we can by default
		break out of a callback loop if only is set to True

		This is mostly to make hateball work the way I want it to
		work.

		'''
		
		irc.IRCClient.msg(self, user, message, length)
		if only:
			raise core.StopCallBacks
		
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
		if re.search(r'^\s*%s\s*[:,]' % self.nickname, msg):
			return re.sub(r'^\s*%s\s*[:,]\s*' % self.nickname, 
				'',
				msg
			)
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
		for mod in MODULES:
			if getattr(sys.modules[mod], 'userJoined', None):
				sys.modules[mod].userJoined(self, user, channel)

	def privmsg(self, user, channel, msg):
		nick = user.split('!', 1)[0]

		try:
			for mod in MODULES:
				if getattr(sys.modules[mod], 'privmsg', None):
					sys.modules[mod].privmsg(self, user, channel, msg)
		except core.StopCallBacks:
			pass

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
			BotFactory(config.nickname, config.channels, 
			config.password), ClientContextFactory())
	else:
		log('Connecting to %s:%i' % (config.host, config.port))
		reactor.connectTCP(config.host, config.port,
			BotFactory(config.nickname, config.channels, 
			config.password))
	reactor.run()
