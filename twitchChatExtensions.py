""" twitchChatExtensions.py
(c) 2018 Matthew J. Ernisse <matt@going-flying.com>
All Rights Reserved.

Handle some esoteric features of the twitch IRC server.

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
"""
import core
from botlogger import debug, err, log, logException


def parseTags(tags):
	""" Parse the tag format and return a dict containing the key/value
	pairs contained within..

	https://ircv3.net/specs/core/message-tags-3.2.html
	"""
	if not tags.startswith("@"):
		return {}

	tagDict = {}
	tagList = tags[1:].split(";")
	for tag in tagList:
		k, v = tag.split("=")
		tagDict[k] = v

	return tagDict


def signedOn(self):
	log("twitchChatExtensions: requesting extra capabilities.")
	self.sendLine("CAP REQ :twitch.tv/commands")
	self.sendLine("CAP REQ :twitch.tv/membership")
	self.sendLine("CAP REQ :twitch.tv/tags")


def unknown(self, prefix, command, params):
	""" Handle twitch CAP tags and re-inject them into the bot to be handled
	as regular IRC events...

	https://dev.twitch.tv/docs/irc/tags/
	"""
	if not command.startswith("@"):
		return

	try:
		paramList = params[0].split(maxsplit=3)
		tags = parseTags(command)
	except Exception as e:
		logException(e)
		return

	if len(paramList) == 2:
		# Looks like GLOBALUSERSTATE is only 2
		usermask, command = paramList
		return

	if len(paramList) == 3:
		usermask, command, target = paramList
		# ROOMSTATE and USERSTATE commands are 3...
		return

	elif len(paramList) == 4:
		# ACTION, CLEARCHAT, and PRIVMSG, USERNOTICE
		usermask, command, target, message = paramList
		message = message[1:]
		if message.startswith("\x01ACTION"):
			# ':\x01ACTION dances\x01'
			message = message[8:-1]
			self.action(usermask, target, message)

		elif command == "PRIVMSG":
			self.privmsg(usermask, target, message, tags)

		else:
			log("unknown twitch command received: {}".format(paramList))


core.MODULES.append(__name__)
