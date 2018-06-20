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
import unittest

import twitchNotifier
from twitchApi import Stream

sys.path.append("tests")
import utils


class TwitchTests(unittest.TestCase):
	def setUp(self):
		self.bot = utils.StubIrcRobot()
		self.twitchClient = utils.StubTwitchClient("")

		twitchNotifier.config = utils.StubConfig()
		twitchNotifier.STREAMS = [
			Stream(self.twitchClient, "test1", 0),
			Stream(self.twitchClient, "test2", 0)
		]

	def testTwitchUsersLive(self):
		twitchNotifier.periodic(self.bot)
		self.assertEqual(
			[
				("testclient", "test1 is streaming Test Stream"),
				("testclient", "test2 is streaming Test Stream 2")
			],
			self.bot.messages
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
		self.twitchClient._getStreamingStatusReply["data"].pop()
		self.twitchClient._getStreamingStatusReply["data"].append(_newStream)

		twitchNotifier.periodic(self.bot)
		self.assertEqual(
			[("testclient", "test2 is streaming Test Stream 3")],
			self.bot.messages
		)

	def testTwitchUsersNoDupeNotification(self):
		twitchNotifier.periodic(self.bot)
		for stream in twitchNotifier.STREAMS:
			self.assertIsInstance(
				stream.lastNotification,
				twitchNotifier.Notification
			)

		self.bot.clear()
		twitchNotifier.periodic(self.bot)
		self.assertEqual([], self.bot.messages)

	def testTwitchUsersStopNotification(self):
		twitchNotifier.periodic(self.bot)
		self.bot.clear()
		self.twitchClient._getStreamingStatusReply["data"].pop()

		twitchNotifier.periodic(self.bot)
		self.assertEqual(
			[("testclient", "test2 has stopped streaming.")],
			self.bot.messages
		)
