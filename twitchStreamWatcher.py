""" twitchStreamWatcher.py (c) 2018 Matthew J. Ernisse <matt@going-flying.com>
All Rights Reserved.

Keep some information about a particular stream around in case someone is
asking questions.

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
import datetime
import requests
import time
import twitchApi
import urllib.parse
from botlogger import err, log, logException

STREAM = None


def privmsg(self, user, channel, msg):
	if channel == self.nickname:
		return

	strippedMsg = self._forMe(msg)
	if not strippedMsg and not msg.startswith("!"):
		return

	if strippedMsg:
		msg = strippedMsg

	if msg.startswith("!"):
		msg = msg[1:]

	if msg == "uptime":
		self.msg(channel, STREAM.uptime)

	elif msg == "topic":
		self.msg(channel, "The current stream is {}".format(STREAM.title))

	else:
		return


config = core.config.getChildren("twitch")
twitchClient = twitchApi.TwitchClient(config.getStr("client_id"))
twitchUserName = config.getStr("username")
STREAM = twitchApi.Stream(twitchClient, twitchUserName)
core.register_module(__name__)
