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
import hateball
import nethack
import topic
import twitchNotifier
import pom

sys.path.append("tests")
import utils

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

	@classmethod
	def setUpClass(cls):
		cls.config = core.Configuration("tests/test.json")

	def testConfigurationBool(self):
		self.assertEqual(
			self.config.getBool("ssl"),
			bool(self._wholeConfig["ssl"])
		)

	def testConfigurationBoolDefault(self):
		self.assertEqual(self.config.getBool("nonExistant"), None)

	def testConfigurationChildren(self):
		children = self.config.getChildren("module")
		self.assertEqual(
			children.config,
			self._wholeConfig["module"]
		)

	def testConfigirationChildrenThrows(self):
		with self.assertRaises(KeyError):
			self.config.getChildren("nonExistant")

	def testConfigurationInt(self):
		self.assertEqual(
			self.config.getInt("port"),
			int(self._wholeConfig["port"])
		)

	def testConfigurationIntDefault(self):
		self.assertEqual(
			self.config.getInt("nonExistant", 12345),
			12345
		)

	def testConfigurationIntThrows(self):
		with self.assertRaises(KeyError):
			self.config.getInt("nonExistant")

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


class HateballTests(unittest.TestCase):
	def setUp(self):
		self.bot = utils.StubIrcRobot()

	def testHateball(self):
		hateball.privmsg(self.bot, "test", "#test", "testbotnick: test")
		self.assertNotEqual(self.bot.messages, [])
		self.assertTrue(self.bot.messages[0][2])

	def testQuietIfNotMe(self):
		hateball.privmsg(self.bot, "test", "#test", "test")
		self.assertEqual(self.bot.messages, [])


class NethackTests(unittest.TestCase):
	def setUp(self):
		self.bot = utils.StubIrcRobot()
		self.pom1 = lambda: 1 
		self.pom50 = lambda: 50
		self.pom100 = lambda: 100

		nethack.NH_FIRED = {}
		nethack.config = utils.StubConfig()

	def testFullMoon(self):
		nethack.pom = self.pom100
		nethack.privmsg(self.bot, "test", "#test", "testbotnick: test message")
		self.assertNotEqual(self.bot.messages, [])

	def testNewMoon(self):
		nethack.pom = self.pom1
		nethack.privmsg(self.bot, "test", "#test", "testbotnick: test message")
		self.assertNotEqual(self.bot.messages, [])

	def testNotDirectedIsQuiet(self):
		nethack.pom = self.pom100
		nethack.privmsg(self.bot, "testuser", "#testchannel", "test message")
		self.assertEqual(self.bot.messages, [])

	def testOtherMoonQuiet(self):
		nethack.pom = self.pom50
		nethack.privmsg(self.bot, "test", "#test", "testbotnick: test message")
		self.assertEqual(self.bot.messages, [])

	def testTooFastIsQuiet(self):
		nethack.config.config["backoff"] = 999999999
		nethack.pom = self.pom100
		nethack.privmsg(self.bot, "test", "#test", "testbotnick: test message")
		self.assertNotEqual(self.bot.messages, [])

		self.bot.clear()
		nethack.privmsg(self.bot, "test", "#test", "testbotnick: test message")
		self.assertEqual(self.bot.messages, [])


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
	def setUp(self):
		self.thisMonth = time.strftime("%m")
		self.thisDay = time.strftime("%d")
		self.mmddKey = "{}-{}".format(self.thisMonth, self.thisDay)
		topic.EVENTS = {self.mmddKey: ["Test Data."]}

	def testTopicUpdaterNoTopic(self):
		testSelf = utils.StubIrcRobot()
		topic.topicUpdated(testSelf, "", "#test", "")

		self.assertEqual(
			testSelf.topicResult[1],
			"{}/{} Test Data.".format(self.thisMonth, self.thisDay)
		)

		self.assertEqual(
			testSelf.topicResult[0],
			"#test"
		)

	def testTopicNotUpdatedIfSet(self):
		currTopic = "This is an already set topic."
		testSelf = utils.StubIrcRobot()
		topic.topicUpdated(testSelf, "", "#test", currTopic)
		self.assertEqual(testSelf.topicResult, "")


class TwitchTests(unittest.TestCase):
	def setUp(self):
		self.bot = utils.StubIrcRobot()
		twitchNotifier.config = utils.StubConfig()
		twitchNotifier.twitchClient = utils.StubTwitchClient("")
		twitchNotifier.STREAMS = [
			twitchNotifier.Stream("test1"),
			twitchNotifier.Stream("test2")
		]

	def testTwitchUsersLive(self):
		twitchNotifier.periodic(self.bot)
		self.assertEqual(
			self.bot.messages,
			[
				("testclient", "test1 is streaming Test Stream"),
				("testclient", "test2 is streaming Test Stream 2")
			]
		)

	def testTwitchUserNewStream(self):
		_newStream = {
			"id": "2",
			"user_id": "1234567891",
			"game_id": "458688",
			"community_ids": [],
			"type": "live",
			"title": "Test Stream 3",
			"viewer_count": 1,
			"started_at": "2018-06-08T12:56:30Z",
			"language": "en",
			"thumbnail_url": "bar"
		}
		twitchNotifier.periodic(self.bot)
		self.bot.clear()

		twitchNotifier.twitchClient._getStreamingStatusReply["data"].pop()
		twitchNotifier.twitchClient._getStreamingStatusReply["data"].append(_newStream)
		for stream in twitchNotifier.STREAMS:
			stream.lastChecked = 0

		twitchNotifier.periodic(self.bot)
		self.assertEqual(
			self.bot.messages,
			[("testclient", "test2 is streaming Test Stream 3")]
		)

	def testTwitchUsersNoDupeNotification(self):
		twitchNotifier.periodic(self.bot)
		for stream in twitchNotifier.STREAMS:
			self.assertIsInstance(
				stream.lastNotification,
				twitchNotifier.Notification
			)
			stream.lastChecked = 0

		self.bot.clear()
		twitchNotifier.periodic(self.bot)
		self.assertEqual(self.bot.messages, [])

	def testTwitchUsersStopNotification(self):
		twitchNotifier.periodic(self.bot)
		self.bot.clear()

		twitchNotifier.twitchClient._getStreamingStatusReply["data"].pop()
		for stream in twitchNotifier.STREAMS:
			stream.lastChecked = 0

		twitchNotifier.periodic(self.bot)
		self.assertEqual(
			self.bot.messages,
			[("testclient", "test2 has stopped streaming.")]
		)
