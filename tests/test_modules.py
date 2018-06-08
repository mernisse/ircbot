#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
'''test_modules.py (c) 2018 Matthew J Ernisse <matt@going-flying.com>
All Rights Reserved.

Unit tests for the irc bot modules.

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
import sys
import time
import json
import unittest

import core
import topic
import twitchNotifier
import pom


class ConfigurationTests(unittest.TestCase):
	_wholeConfig = {
		"ssl": "true",
		"nickname": "test",
		"port": "6969",
		"channels": [
			"#test1",
			"#test2",
		],
		"password": "private",
		"module": {
			"key": [
				"someval",
			],
		},
	}

	def setUp(self):
		self.config = core.Configuration("tests/test.json")

	def testConfigurationBool(self):
		self.assertEqual(
			self.config.getBool("ssl"),
			bool(self._wholeConfig["ssl"])
		)

	def testConfigurationChildren(self):
		children = self.config.getChildren("module")
		self.assertEqual(
			children.config,
			self._wholeConfig["module"]
		)

	def testConfigurationInt(self):
		self.assertEqual(
			self.config.getInt("port"),
			int(self._wholeConfig["port"])
		)

	def testConfigurationLoads(self):
		self.assertEqual(self.config.config, self._wholeConfig)

	def testConfigurationList(self):
		self.assertEqual(
			self.config.getList("channels"),
			self._wholeConfig["channels"]
		)

	def testConfigirationStr(self):
		self.assertEqual(
			self.config.getStr("password"),
			self._wholeConfig["password"]
		)


class PomTests(unittest.TestCase):
	def testKnownFullMoon(self):
		# May 30 2018 00:00 GMT
		time_t = time.gmtime(1527638400)
		result = int(pom.potm(time_t))
		self.assertEqual(result, 99)

	def testKnownNewMoon(self):
		# June 14 2018 00:00 GMT
		time_t = time.gmtime(1528934400)
		result = int(pom.potm(time_t))
		self.assertEqual(result, 0)


class TopicTests(unittest.TestCase):
	class TopicCatcher(object):
		""" Stub class for the topic methods. """
		result = ""

		def topic(self, channel, event):
			self.result = (channel, event)

	def setUp(self):
		self.thisMonth = time.strftime("%m")
		self.thisDay = time.strftime("%d")
		self.mmddKey = "{}-{}".format(self.thisMonth, self.thisDay)
		topic.EVENTS = {self.mmddKey: ["Test Data."]}

	def testTopicUpdaterNoTopic(self):
		testSelf = self.TopicCatcher()
		topic.topicUpdated(testSelf, "", "#test", "")

		self.assertEqual(
			testSelf.result[1],
			"{}/{} Test Data.".format(self.thisMonth, self.thisDay)
		)

		self.assertEqual(
			testSelf.result[0],
			"#test"
		)

	def testTopicNotUpdatedIfSet(self):
		currTopic = "This is an already set topic."
		testSelf = self.TopicCatcher()
		topic.topicUpdated(testSelf, "", "#test", currTopic)
		self.assertEqual(testSelf.result, "")


class TwitchTests(unittest.TestCase):
	class StubConfig(object):
		""" Stub out the configuration object."""
		config = {
			"users": ["testclient"],
		}

		def getList(self, key):
			return self.config[key]

	class StubTwitchClient(object):
		""" Override for the twitch client class"""
		_getStreamingStatusReply = '''{
			"data":[
				{
					"id":"0",
					"user_id":"1234567890",
					"game_id":"458688",
					"community_ids":[],
					"type":"live",
					"title":"Test Stream",
					"viewer_count":1,
					"started_at":"2018-06-08T12:56:28Z",
					"language":"en",
					"thumbnail_url":"foo"
				},
				{
					"id":"1",
					"user_id":"1234567891",
					"game_id":"458688",
					"community_ids":[],
					"type":"live",
					"title":"Test Stream 2",
					"viewer_count":1,
					"started_at":"2018-06-08T12:56:28Z",
					"language":"en",
					"thumbnail_url":"bar"
				}
			],
			"pagination":{
				"cursor":""
			}
		}'''

		def __init__(self, clientId):
			pass

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
			return json.loads(self._getStreamingStatusReply)["data"]

	class StubIrcRobot(object):
		""" Stub class to get msg calls from the notifier plugin"""
		def __init__(self):
			self.messages = []

		def clear(self):
			""" Clear messages list """
			self.messages = []

		def msg(self, user, message):
			self.messages.append((user, message))

	def setUp(self):
		self.stubIrcRobot = self.StubIrcRobot()
		twitchNotifier.config = self.StubConfig()
		twitchNotifier.twitchClient = self.StubTwitchClient("")
		twitchNotifier.STREAMS = [
			twitchNotifier.Stream("test1"),
			twitchNotifier.Stream("test2")
		]

	def testTwitchUsersLive(self):
		twitchNotifier.periodic(self.stubIrcRobot)
		self.assertEqual(
			self.stubIrcRobot.messages,
			[
				("testclient", "test1 is streaming Test Stream"),
				("testclient", "test2 is streaming Test Stream 2")
			]
		)

	def testTwitchUsersNoDupeNotification(self):
		twitchNotifier.periodic(self.stubIrcRobot)
		self.stubIrcRobot.clear()
		twitchNotifier.periodic(self.stubIrcRobot)
		self.assertEqual(self.stubIrcRobot.messages, [])
		for stream in twitchNotifier.STREAMS:
			self.assertTrue(isinstance(
				stream.lastNotification,
				twitchNotifier.Notification
			))


if __name__ == "__main__":
	unittest.main()
