""" twitchApi.py (c) 2018 Matthew J. Ernisse <matt@going-flying.com>
All Rights Reserved.

Implement the Twitch "New Api".
https://dev.twitch.tv/docs/api/reference/

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
import datetime
import requests
import time
import urllib.parse


class Stream(object):
	""" Hold state of a Twitch stream. """
	def __init__(self, twitchClient, twitchUsername, checkMinutes=1):
		self._checkMinutes = checkMinutes
		self._lastChecked = 0
		self._title = ""
		self._userId = ""
		self.live = False
		self.started = 0
		self.twitchClient = twitchClient
		self.twitchUsername = twitchUsername

	def _reloadIfExpired(self):
		""" Reload the values from the API if they have expired. """
		now = time.time()
		if (now - self._lastChecked) < self._checkMinutes * 60:
			return

		try:
			status = self.twitchClient.getStreamingStatus(self.userId)
		except Exception:
			return

		if not status:
			return

		if status[0]["type"] == "live":
			self.live = True
			self.started = self.twitchClient.dateStringToSecs(
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
			self._userId = self.twitchClient.getUserId(self.twitchUsername)
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
	""" Super minimal implementation of the New Twitch API."""
	_baseUrl = "https://api.twitch.tv/helix/"

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
			apiUrl = urllib.parse.urljoin(self._baseUrl, url)
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