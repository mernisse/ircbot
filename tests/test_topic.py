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
import unittest

import topic

sys.path.append("tests")
import utils


class TopicTests(unittest.TestCase):
	def setUp(self):
		self.bot = utils.StubIrcRobot()
		self.thisMonth = time.strftime("%m")
		self.thisDay = time.strftime("%d")
		self.mmddKey = "{}-{}".format(self.thisMonth, self.thisDay)
		topic.EVENTS = {self.mmddKey: ["Test Data."]}

	def testTopicChanges(self):
		currTopic = "00/00 This is an old topic."
		topic.topicUpdated(self.bot, "", "#test", currTopic)

		self.assertEqual(
			self.bot.topicResult[1],
			"{}/{} Test Data.".format(self.thisMonth, self.thisDay)
		)

		self.assertEqual(
			self.bot.topicResult[0],
			"#test"
		)

	def testTopicNotUpdatedIfSet(self):
		currTopic = "This is an already set topic."
		topic.topicUpdated(self.bot, "", "#test", currTopic)
		self.assertEqual(self.bot.topicResult, "")

	def testTopicNotUpdatedIfToday(self):
		currTopic = "{}/{} Test Data.".format(self.thisMonth, self.thisDay)
		topic.topicUpdated(self.bot, "", "#test", currTopic)
		self.assertEqual(self.bot.topicResult, "")

	def testTopicUpdatesIfNoTopic(self):
		topic.topicUpdated(self.bot, "", "#test", "")

		self.assertEqual(
			self.bot.topicResult[1],
			"{}/{} Test Data.".format(self.thisMonth, self.thisDay)
		)

		self.assertEqual(
			self.bot.topicResult[0],
			"#test"
		)

	def testTopicTriesRss(self):
		expected = ("#test", "{}/{} Nothing ever happens.".format(
			self.thisMonth,
			self.thisDay
		))
		topic.EVENTS = {}
		topic.load_alternate_rss = lambda x: None
		topic.topicUpdated(self.bot, "", "#test", "")
		self.assertEqual(self.bot.topicResult, expected)
