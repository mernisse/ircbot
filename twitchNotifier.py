''' twitch-notifier.py (c) 2018 Matthew J. Ernisse <matt@going-flying.com>
All Rights Reserved.

Notify me if someone starts streaming.

'''

import core
import requests
import time
from botlogger import *

import urllib.parse

CHECK_MINS = 15
LAST_CHECK = 0
STREAMS = []

class Stream(object):
	""" Hold state of a Twitch stream. """
	def __init__(self, twitchUsername):
		self.twitchUsername = twitchUsername
		self.userId = twitchClient.getUserId(twitchUsername)
		self.lastChecked = 0
		self.lastNotification = None

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

		if self.userId == other.userId and \
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
		# 2017-08-14T15:45:17Z
		return time.mktime(
			time.strptime(
				dateString,
				"%Y-%m-%dT%H:%M:%SZ"
			)
		)

class TwitchClient(object):
	""" Super minimal implementation of a New Twitch API client."""
	baseUrl = "https://api.twitch.tv/helix/"

	def __init__(self, clientId):
		self.clientId = clientId

	def getUserId(self, userName):
		jsonStatus = self._fetch("users", {
			"login": userName
		})

		if not jsonStatus["data"]:
			raise ValueError("Username not found.")

		return jsonStatus["data"][0]["id"]

	def getStreamingStatus(self, userId):
		if not type(userId) == list:
			userId = [userId]

		jsonStatus = self._fetch('streams', {
			"user_id": userId,
		})

		if not jsonStatus:
			return None

		if not jsonStatus["data"]:
			return None

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
				params=args
			)
			response.raise_for_status()
			return response.json()
		except Exception as e:
			logException(e)
			return None


def periodic(self):
	global CHECK_MINS, STREAMS
	now = time.time()
	toCheck = []

	for twitchStream in STREAMS:
		if (now - twitchStream.lastChecked) < (CHECK_MINS * 60):
			continue

		toCheck.append(twitchStream.userId)
		twitchStream.lastChecked = now

	if not toCheck:
		return

	status = twitchClient.getStreamingStatus(toCheck)
	if not status:
		return

	for twitchStream in status:
		userId = twitchStream["user_id"]
		title = twitchStream["title"]
		started = twitchStream["started_at"]

		stream = None
		for s in STREAMS:
			if s.userId == userId:
				stream = s
				break

		newNotification = Notification(
			stream.twitchUsername,
			started,
			title
		)

		if stream.lastNotification == newNotification:
			debug("skipping already sent notification.")
			continue

		stream.lastNotification = newNotification
		for user in config.getList("users"):
			self.msg(user, "{} is streaming {}".format(
				stream.twitchUsername,
				title
			))

config = core.config.getChildren("twitch")
twitchClient = TwitchClient(config.getStr("client_id"))
for twitchUsername in config.getList("streams"):
	STREAMS.append(Stream(twitchUsername))

core.register_module(__name__)
