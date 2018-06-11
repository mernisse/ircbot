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
import urllib.parse
from botlogger import err, log, logException

CHECK_MINS = 1
LAST_CHECK = 0
STREAM = None


class Stream(object):
	""" Hold state of a Twitch stream. """
	def __init__(self, twitchUsername):
		self.live = False
		self.started = 0
		self._title = ""
		self._userId = ""
		self.twitchUsername = twitchUsername
		self.lastChecked = 0

	def _reloadIfExpired(self):
		""" Reload the values from the API if they have expired. """
		now = time.time()
		if (now - self.lastChecked) < CHECK_MINS * 60:
			return

		try:
			status = twitchClient.getStreamingStatus(self.userId)
		except Exception:
			return

		if not status:
			return

		if status[0]["type"] == "live":
			self.live = True
			self.started = twitchClient.dateStringToSecs(
				status[0]["started_at"]
			)
			self._title = status[0]["title"]

		else:
			self.live = False
			self.started = 0
			self._title = ""

	@property
	def title(self):
		self._reloadIfExpired()
		if not self.live:
			return "not live."

		self._title

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

	@property
	def uptime(self):
		self._reloadIfExpired()
		if not self.live:
			return "No current stream."

		elapsed = time.time() - self.started_at
		mins, secs = divmod(elapsed, 60)
		hours, mins = divmod(mins, 60)
		days, hours = divmod(hours, 24)
		weeks, days = divmod(days, 7)

		if weeks:
			return "{} wk, {} days, {}:{}:{}".format(
				weeks,
				days,
				hours,
				mins,
				secs
			)

		if days:
			return "{} days, {}:{}:{}".format(
				days,
				hours,
				mins,
				secs
			)

		if hours > 1:
			return "{} hours, {}:{}".format(
				hours,
				mins,
				secs
			)

		elif hours == 1:
			return "{} hour, {}:{}".format(
				hours,
				mins,
				secs
			)

		if mins > 1:
			return "{} minutes, {} seconds".format(
				mins,
				secs
			)
		elif mins == 1:
			return "{} minutes, {} seconds".format(
				mins,
				secs
			)

		return "{} seconds".format(secs)


class TwitchAPIError(Exception):
	pass


class TwitchClient(object):
	""" Super minimal implementation of a New Twitch API client."""
	baseUrl = "https://api.twitch.tv/helix/"

	def __init__(self, clientId):
		self.clientId = clientId

	def dateStringToSecs(self, dateString):
		""" Convert Twitch date/time strings to epoch seconds. """
		# 2017-08-14T15:45:17Z
		return time.mktime(
			time.strptime(
				dateString,
				"%Y-%m-%dT%H:%M:%SZ"
			)
		)

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
				timeout=1
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
twitchClient = TwitchClient(config.getStr("client_id"))
twitchUserName = config.getStr("username")
STREAM = Stream(twitchUserName)
core.register_module(__name__)
