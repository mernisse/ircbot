''' bot.py (c) 2013 - 2018 Matthew Ernisse <matt@going-flying.com>
All Rights Reserved

This is the main module of the IRC robot.  I envision him as Marvin, The
Paranoid Android.

He is built on the Twisted framework.

The bot accepts the following commands:
reload <module> - This will reload the python module specified.
join <channel> - This will join the specified channel.
leave <channel> - This will part the specified channel.

Commands must be issued via a PRIVMSG to the bot from someone listed in
config.owners.

Marvin has a brain the size of a planet, it is implemented in core.py.

Redistribution and use in source and binary forms,
with or without modification, are permitted provided
that the following conditions are met:

    * Redistributions of source code must retain the
      above copyright notice, this list of conditions
      and the following disclaimer.
    * Redistributions in binary form must reproduce
      the above copyright notice, this list of conditions
      and the following disclaimer in the documentation
      and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS
OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR
TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE
USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''
import re
import sys
import time

from botlogger import debug, err, log, logException
from twisted.internet import protocol, reactor, task
from twisted.words.protocols import irc

import core


class Bot(irc.IRCClient):
	""" This is the robot. """
	sourceURL = "https://github.com/mernisse/ircbot"
	versionEnv = "Python"
	versionName = "Marvin"

	@property
	def nickname(self):
		return self.factory.nickname

	@nickname.setter
	def nickname(self, value):
		if not self.factory:
			raise Exception("Cannot set value until factory assignment.")
		self.factory.nickname = value

	@property
	def realname(self):
		return self.factory.realname

	@property
	def password(self):
		return self.factory.password

	@property
	def username(self):
		return self.factory.nickname

	@property
	def versionNum(self):
		return core.__version__

	def _forMe(self, msg):
		''' determine if a message was sent to me, if it was strip
		my nick off the front of it and just return the payload.

		'''
		if re.search(r'^\s*%s\s*[:,]' % self.nickname, msg):
			return re.sub(
				r'^\s*%s\s*[:,]\s*' % self.nickname,
				'',
				msg)
		return False

	def connectionMade(self):
		super().connectionMade()
		self.chatters = {}
		self.debug = self.factory.config.getBool("debug")
		self.owners = self.factory.config.getList("owners")
		self.task = None
		self.channels = self.factory.config.getList("channels")
		log("connection established.")

		for mod in core.MODULES:
			if getattr(sys.modules[mod], 'connectionMade', None):
				sys.modules[mod].connectionMade(self)

	def connectionLost(self, reason):
		log("Connection closed: {}".format(reason.getErrorMessage()))
		try:
			self.task.stop()
		except Exception as e:
			pass

		for mod in core.MODULES:
			if getattr(sys.modules[mod], 'connectionLost', None):
				sys.modules[mod].connectionLost(self)

	#
	# Actions
	#
	def names(self, channel):
		''' Get a userlist for the channel, on reply namesReply() will
		be called.  Can be disabled (eg: for twitch irc).
		'''
		if not self.factory.config.getBool("namesNotSupported"):
			channel = channel.lower()
			self.sendLine("NAMES %s" % channel)

	def msg(self, user, message, length=None, only=None):
		''' Overload irc.IRCClient.msg() so that we can break out of
		a callback loop if only is set to True.

		This is mostly to make hateball work the way I want it to
		work.
		'''
		if not message:
			if only:
				raise core.StopCallBacks

			return

		super().msg(user, message, length)
		if only:
			raise core.StopCallBacks

	#
	# Event Callbacks.
	#
	def action(self, user, channel, msg):
		''' Called on a CTCP ACTION '''
		for mod in core.MODULES:
			if getattr(sys.modules[mod], 'action', None):
				sys.modules[mod].action(
					self,
					user,
					channel,
					msg
				)

	def joined(self, channel):
		''' Called when we join a channel. '''
		if channel not in self.channels:
			self.channels.append(channel)

		self.chatters[channel] = {'users': {}}
		self.names(channel)

		for mod in core.MODULES:
			if getattr(sys.modules[mod], 'joined', None):
				sys.modules[mod].joined(self, channel)

	def left(self, channel):
		''' Called when we leave a channel '''
		log('Left channel %s' % channel)
		self.chatters.pop(channel)
		self.channels.remove(channel)

		for mod in core.MODULES:
			if getattr(sys.modules[mod], 'left', None):
				sys.modules[mod].left(self, channel)

	def modeChanged(self, user, channel, set, modes, args):
		''' Called on a server/user/channel mode change '''
		if channel.startswith("#"):
			self.names(channel)

		for mod in core.MODULES:
			if not getattr(sys.modules[mod], 'modeChanged', None):
				continue

			sys.modules[mod].modeChanged(
				self,
				user,
				channel,
				set,
				modes,
				args
			)

	def noticed(self, user, channel, message):
		''' Called when we receive a NOTICE, per the RFC
		we MUST NEVER programatically respond to a notice.

		No module callbacks are called from this.
		'''
		log('NOTICE - %s in %s: %s' % (
			user, channel, message))

	def periodic(self):
		''' This is called every 5 minutes. '''
		for mod in core.MODULES:
			if getattr(sys.modules[mod], 'periodic', None):
				try:
					sys.modules[mod].periodic(self)
				except Exception as e:
					logException(e)

	def privmsg(self, user, channel, msg):
		''' Called when the bot sees a message in a channel or receives
		a query.

		Bot control actions should go into the privmsg callback in
		core.py.
		'''
		try:
			for mod in core.MODULES:
				if getattr(sys.modules[mod], 'privmsg', None):
					sys.modules[mod].privmsg(self, user, channel, msg)

		except core.StopCallBacks:
			pass

		except Exception as e:
			logException(e)

	def signedOn(self):
		''' Called upon successful connection to the server '''
		log('Joining %s' % ",".join(self.channels))
		#
		# we want to fire a callback every 5 minutes, just in case we
		# want that for various module functionality.
		#
		if not self.task:
			self.task = task.LoopingCall(self.periodic)
			self.task.start(5 * 60)

		#
		# Make it so we can get the bot's nick without
		# having to have the bot's object.
		#
		core.nickname = self.nickname

		for mod in core.MODULES:
			if getattr(sys.modules[mod], 'signedOn', None):
				try:
					sys.modules[mod].signedOn(self)
				except Exception as e:
					logException(e)

		for chan in self.channels:
			self.join(chan)

	def topicUpdated(self, user, channel, newtopic):
		''' Called when a channel topic is updated. '''
		for mod in core.MODULES:
			if not getattr(sys.modules[mod], 'topicUpdated', None):
				continue

			sys.modules[mod].topicUpdated(
				self,
				user,
				channel,
				newtopic
			)

	def userJoined(self, user, channel):
		''' Called when a user joins a channel. '''
		self.chatters[channel]['users'].update({
			user: {}
		})
		self.whois(user)

		for mod in core.MODULES:
			if getattr(sys.modules[mod], 'userJoined', None):
				sys.modules[mod].userJoined(self, user, channel)

	def userKicked(self, kickee, channel, kicker, message):
		''' Called when a user KICKs another user. '''
		log('observed %s kick %s from %s for %s'.format(
			kicker, kickee, channel, message
		))

		self.chatters[channel]['users'].pop(kickee)

		for mod in core.MODULES:
			if getattr(sys.modules[mod], 'userKicked', None):
				sys.modules[mod].userKicked(
					self,
					kickee,
					channel,
					kicker,
					message
				)

	def userLeft(self, user, channel):
		''' Called when a user PARTs a channel. '''
		try:
			self.chatters[channel]['users'].pop(user)
		except KeyError as e:
			err('mystery user %s left %s' % (user, channel))

		for mod in core.MODULES:
			if getattr(sys.modules[mod], 'userLeft', None):
				sys.modules[mod].userLeft(self, user, channel)

	def userQuit(self, user, message):
		''' Called when a user QUITs IRC. '''
		for channel in self.chatters:
			if user in self.chatters[channel]:
				self.chatters[channel]['users'].pop(user)

		for mod in core.MODULES:
			if getattr(sys.modules[mod], 'userQuit', None):
				sys.modules[mod].userQuit(self, user, message)

	def userRenamed(self, oldname, newname):
		''' Called when a user changes his/her nick. '''
		for chan in self.chatters:
			try:
				oldchatter = self.chatters[chan]['users'].pop(oldname)
			except KeyError:
				oldchatter = {}

			self.chatters[chan]['users'][newname] = oldchatter

		for mod in core.MODULES:
			if getattr(sys.modules[mod], 'userRenamed', None):
				sys.modules[mod].userRenamed(
					self,
					oldname,
					newname
				)

	#
	# IRC Protocol Handler Callbacks.
	#
	def irc_RPL_NAMREPLY(self, prefix, params):
		''' Handle the NAMES reply. '''
		channel = params[2].lower()
		nicklist = params[3].split(' ')

		if channel not in self.chatters:
			return

		for nick in nicklist:
			if nick in self.chatters[channel]['users']:
				continue

			if nick.startswith('@'):
				nick = nick[1:]

			self.chatters[channel]['users'].update({
				nick: {}
			})

	def irc_RPL_ENDOFNAMES(self, prefix, params):
		''' Called when a NAMES reply is finished '''
		channel = params[1].lower()

		if channel not in self.chatters:
			err('NAMES reply for %s which is not in chatters' % (
				channel))
			return

		for user in self.chatters[channel]['users']:
			self.whois(user)

		for mod in core.MODULES:
			if not getattr(sys.modules[mod], 'namesReply', None):
				continue

			sys.modules[mod].namesReply(
				self,
				channel,
				self.chatters[channel]['users'].keys()
			)

	def irc_RPL_WHOISIDLE(self, prefix, params):
		''' Called for the IDLE portion of the WHOIS reply '''
		user = params[1]

		for channel in self.chatters:
			if user not in self.chatters[channel]['users']:
				continue

			info = {
				'idle': params[2],
				'signOn': params[3],
			}
			self.chatters[channel]['users'][user].update(info)

	def irc_RPL_WHOISUSER(self, prefix, params):
		''' Called for the USER portion of the WHOIS reply '''
		user = params[1]

		for channel in self.chatters:
			if user not in self.chatters[channel]['users']:
				continue

			info = {
				'username': params[2],
				'hostname': params[3],
				'realname': params[5],
			}
			self.chatters[channel]['users'][user].update(info)

	def irc_RPL_ENDOFWHOIS(self, prefix, params):
		''' Called when a WHOIS reply is finished '''
		user = params[1]

		for channel in self.chatters:
			if user not in self.chatters[channel]['users']:
				continue

			info = self.chatters[channel]['users'][user]
			break
		else:
			return

		for mod in core.MODULES:
			if getattr(sys.modules[mod], 'whoisReply', None):
				sys.modules[mod].whoisReply(self, user, info)

	def irc_unknown(self, prefix, command, params):
		''' Called on any unhandled server replies '''
		# Uncomment to log any unhandled replies from the server.
		if self.debug:
			log('UNKN: prefix=%s, command=%s, params=%s' % (
				prefix, command, params))


class BotFactory(protocol.ReconnectingClientFactory):
	protocol = Bot

	def __init__(self, config):
		self.config = config
		self.nickname = config.getStr("nickname")
		self.password = config.getStr("password")
		self.realname = config.getStr("realname")

	def clientConnectionLost(self, connector, reason):
		super().clientConnectionLost(connector, reason)

	def clientConnectionFailed(self, connector, reason):
		super().clientConnectionFailed(connector, reason)
