""" twitch-notifier.py (c) 2018 Matthew J. Ernisse <matt@going-flying.com>
All Rights Reserved.

Notify me if someone starts streaming.

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
import requests
import time
import twitchApi
import urllib.parse
from botlogger import err, log, logException

CHECK_MINS = 15
STREAMS = []


class Notification(object):
	""" Hold state of Notifications sent to IRC users so we do not
	continue notifying on a stream over and over again.
	"""
	def __init__(self, twitchUsername, started, streamName):
		self.twitchUsername = twitchUsername
		self.started = started
		self.streamName = streamName

	def __eq__(self, other):
		if not isinstance(other, self.__class__):
			return False

		if self.twitchUsername == other.twitchUsername and \
			self.streamName == other.streamName and \
			self.started == other.started:
			return True

		return False

	def __repr__(self):
		return "<Notification: {} streaming {} started {}>".format(
			self.twitchUsername,
			self.streamName,
			self.started
		)


def periodic(self):
	""" Iterate through STREAMS and look for streams that are live.
	Uses Notification() to ensure we don't emit a notification more
	than once per stream title/start time.
	"""
	global STREAMS

	for stream in STREAMS:
		# .live does not trigger the refresh, so get title to make sure
		# the object is up-to-date.  Maybe make live trigger a refresh
		# to allow this to not be needed...
		streamTitle = stream.title

		if not stream.live:
			if stream.lastNotification:
				stream.lastNotification = None
				for user in config.getList("users"):
					self.msg(user, "{} has stopped streaming.".format(
						stream.twitchUsername
					))

			continue

		newNotification = Notification(
			stream.twitchUsername,
			stream.started,
			streamTitle
		)

		if stream.lastNotification == newNotification:
			continue

		stream.lastNotification = newNotification
		for user in config.getList("users"):
			self.msg(user, "{} is streaming {}".format(
				stream.twitchUsername,
				streamTitle
			))


config = core.config.getChildren("twitch")
twitchClient = twitchApi.TwitchClient(config.getStr("client_id"))
for twitchUsername in config.getList("streams"):
	STREAMS.append(twitchApi.Stream(
		twitchClient,
		twitchUsername,
		CHECK_MINS
	))

log("twitchNotifier loaded {} streams".format(len(STREAMS)))
core.register_module(__name__)
