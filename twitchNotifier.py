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
import urllib.parse
from botlogger import err, log, logException

CHECK_MINS = 15
LAST_CHECK = 0
STREAMS = []


class Stream(object):
	""" Hold state of a Twitch stream. """
	def __init__(self, twitchUsername):
		self._userId = ""
		self.twitchUsername = twitchUsername
		self.lastChecked = 0
		self.lastNotification = None

	@property
	def userId(self):
		""" Lazy load the userId property. """
		if self._userId:
			return self._userId
		try:
			self._userId = twitchClient.getUserId(self.twitchUsername)
			return self._userId
		except Exception as e:
			err("Cannot resolve Twitch userId for {}".format(
				self.twitchUsername
			))
			return None


class Notification(object):
	""" Hold state of Notifications sent to IRC users so we do not
	continue notifying on a stream over and over again.
	"""
	def __init__(self, twitchUsername, dateString, streamName):
		self.twitchUsername = twitchUsername
		self.started = self.dateStringToSecs(dateString)
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

	def dateStringToSecs(self, dateString):
		""" Convert Twitch date/time strings to epoch seconds. """
		# 2017-08-14T15:45:17Z
		return time.mktime(
			time.strptime(
				dateString,
				"%Y-%m-%dT%H:%M:%SZ"
			)
		)


class TwitchAPIError(Exception):
	pass


class TwitchClient(object):
	""" Super minimal implementation of a New Twitch API client."""
	baseUrl = "https://api.twitch.tv/helix/"

	def __init__(self, clientId):
		self.clientId = clientId

	def getUserId(self, userName):
		""" Resolve a Twitch Username to their userId. """
		jsonStatus = self._fetch("users", {
			"login": userName
		})

		if not jsonStatus or not jsonStatus.get("data", None):
			raise ValueError("Username not found.")

		try:
			userId = jsonStatus["data"][0]["id"]
		except Exception as e:
			logException(e)
			raise ValueError("API failure fetching {}".format(userName))

		return userId

	def getStreamingStatus(self, userId):
		""" Query the Twitch New API for the live streams of the given
		userIds.
		"""
		if not type(userId) == list:
			userId = [userId]

		jsonStatus = self._fetch('streams', {
			"user_id": userId,
		})

		if not jsonStatus:
			return []

		if not jsonStatus.get("data", None):
			return []

		return jsonStatus["data"]

	def _fetch(self, url, args):
		headers = {
			"Client-ID": self.clientId,
		}

		try:
			apiUrl = urllib.parse.urljoin(self.baseUrl, url)
			response = requests.get(
				apiUrl,
				headers=headers,
				params=args,
				timeout=0.3
			)
			response.raise_for_status()
			return response.json()

		except requests.exceptions.Timeout:
			err("_fetch(): timeout connecting to {}".format(apiUrl))
			raise TwitchAPIError("Timeout")

		except requests.exceptions.ConnectionError:
			err("_fetch(): failed to connect to {}".format(apiUrl))
			raise TwitchAPIError("Connection failed")

		except Exception as e:
			logException(e)
			raise TwitchAPIError("General Error")


def periodic(self):
	""" Every CHECK_MINS iterate through STREAMS and see if we should
	notify "twitch"/"users".  Uses Notification() to ensure we don't
	emit a notification more than once per stream title/start time.
	"""
	global CHECK_MINS, STREAMS
	now = time.time()
	toCheck = []

	for twitchStream in STREAMS:
		if (now - twitchStream.lastChecked) < (CHECK_MINS * 60):
			continue

		toCheck.append(twitchStream)
		twitchStream.lastChecked = now

	if not toCheck:
		return

	try:
		status = twitchClient.getStreamingStatus(
			[x.userId for x in toCheck]
		)
	except TwitchAPIError:
		return

	for stream in toCheck:
		for twitchStream in status:
			if twitchStream["user_id"] != stream.userId:
				continue

			newNotification = Notification(
				stream.twitchUsername,
				twitchStream["started_at"],
				twitchStream["title"]
			)

			if stream.lastNotification == newNotification:
				break

			stream.lastNotification = newNotification
			for user in config.getList("users"):
				self.msg(user, "{} is streaming {}".format(
					stream.twitchUsername,
					twitchStream["title"]
				))
			break

		else:
			if stream.lastNotification:
				stream.lastNotification = None
				for user in config.getList("users"):
					self.msg(user, "{} has stopped streaming.".format(
						stream.twitchUsername
					))


config = core.config.getChildren("twitch")
twitchClient = TwitchClient(config.getStr("client_id"))
for twitchUsername in config.getList("streams"):
	STREAMS.append(Stream(twitchUsername))

log("twitchNotifier loaded {} streams".format(len(STREAMS)))
core.register_module(__name__)
