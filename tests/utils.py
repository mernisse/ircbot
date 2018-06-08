#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
'''test_utils.py (c) 2018 Matthew J Ernisse <matt@going-flying.com>
All Rights Reserved.

Mock classes for the test cases.

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
import bot


class StubConfig(object):
	""" Stub out the configuration object."""
	config = {
		"backoff": 0,
		"pom_high": 99,
		"pom_low": 1,
		"users": ["testclient"],
	}

	def getInt(self, key):
		return self.config[key]

	def getList(self, key):
		return self.config[key]

class StubTwitchClient(object):
	""" Override for the twitch client class"""
	def __init__(self, clientId):
		self._getStreamingStatusReply = {
			"data": [
				{
					"id": "0",
					"user_id": "1234567890",
					"game_id": "458688",
					"community_ids": [],
					"type": "live",
					"title": "Test Stream",
					"viewer_count": 1,
					"started_at": "2018-06-08T12:56:28Z",
					"language": "en",
					"thumbnail_url": "foo"
				},
				{
					"id": "1",
					"user_id": "1234567891",
					"game_id": "458688",
					"community_ids": [],
					"type": "live",
					"title": "Test Stream 2",
					"viewer_count": 1,
					"started_at": "2018-06-08T12:56:28Z",
					"language": "en",
					"thumbnail_url": "bar"
				}
			],
			"pagination": {
				"cursor": ""
			}
		}

	def getUserId(self, userName):
		if userName == "test1":
			return "1234567890"

		elif userName == "test2":
			return "1234567891"

		elif userName == "testThrows":
			raise ValueError("Requested Exception")

		else:
			raise ValueError("unknown username specified")

	def getStreamingStatus(self, userId):
		return self._getStreamingStatusReply["data"]

class StubIrcRobot(object):
	""" Stub class for the IRCBot. """
	nickname = "testbotnick"
	def __init__(self):
		self.messages = []
		self.topicResult = ""

	def _forMe(self, nick):
		return bot.Bot._forMe(self, nick)

	def clear(self):
		""" Clear messages list """
		self.messages = []

	def msg(self, user, message, only=None):
		if only:
			self.messages.append((user, message, only))
		else:
			self.messages.append((user, message))

	def topic(self, channel, event):
		self.topicResult = (channel, event)
