""" mixerNotifier.py (c) 2020 Matthew J. Ernisse <matt@going-flying.com>
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
import urllib.parse
from botlogger import err, log, logException

CHECK_MINS = 15
STREAMS = []


class MixerStream(object):
	def __init__(self, mixerUsername, checkMinutes=1):
		self.checkMinutes = checkMinutes
		self.mixerUsername = mixerUsername
		# force a check on startup
		self.lastChecked = time.time() + 86400
		self.lastNotification = 0
		self.url = f'https://mixer.com/api/v1/channels/{mixerUsername}'

		self._title = ''
		self._live = ''
		self._load()

	def _load(self):
		''' Load the status of a stream.'''
		now = time.time()
		if (now - self.lastChecked) < self.checkMinutes * 60:
			return

		self.lastChecked = time.time()

		try:
			resp = requests.get(self.url)
			resp.raise_for_status()
			status = resp.json()
		except Exception:
			return
	
		self._live = status['online']
		self._title = status['name']

	@property
	def live(self):
		self._load()
		return self._live

	@property
	def title(self):
		self._load()
		return self._title


class Notification(object):
	""" Hold state of Notifications sent to IRC users so we do not
	continue notifying on a stream over and over again.
	"""
	def __init__(self, mixerhUsername, started, streamName):
		self.mixerhUsername = mixerUsername
		self.streamName = streamName

	def __eq__(self, other):
		if not isinstance(other, self.__class__):
			return False

		if self.mixerUsername == other.mixerhUsername and \
			self.streamName == other.streamName:
			return True

		return False

	def __repr__(self):
		return "<Notification: {} streaming {}>".format(
			self.mixerUsername,
			self.streamName
		)


def periodic(self):
	""" Iterate through STREAMS and look for streams that are live.
	Uses Notification() to ensure we don't emit a notification more
	than once per stream title/start time.
	"""
	global STREAMS

	for stream in STREAMS:
		if not stream.live:
			if stream.lastNotification:
				stream.lastNotification = None
				for user in config.getList("users"):
					self.msg(user, "{} has stopped streaming.".format(
						stream.mixerUsername
					))

			continue

		newNotification = Notification(
			stream.mixerUsername,
			stream.title
		)

		if stream.lastNotification == newNotification:
			continue

		stream.lastNotification = newNotification
		for user in config.getList("users"):
			self.msg(user, "{} is streaming {}".format(
				stream.mixerUsername,
				streamTitle
			))


config = core.config.getChildren("mixer")

for mixerUsername in config.getList("streams"):
	STREAMS.append(MixerStream(
		mixerUsername,
		CHECK_MINS
	))

log("mixerNotifier loaded {} streams".format(len(STREAMS)))
core.register_module(__name__)
