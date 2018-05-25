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

sys.path.append("..")

import topic
import pom


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

	def testTopicUpdaterNoTopic(self):
		thisMonth = time.strftime("%m")
		thisDay = time.strftime("%d")
		key = "{}-{}".format(thisMonth, thisDay)
		topic.EVENTS = {key: ["Test Data."]}
		testSelf = self.TopicCatcher()
		topic.topicUpdated(testSelf, "", "#test", "")

		self.assertEqual(
			testSelf.result[1],
			"{}/{} Test Data.".format(thisMonth, thisDay)
		)

		self.assertEqual(
			testSelf.result[0],
			"#test"
		)

	def testTopicNotUpdatedIfSet(self):
		currTopic = "This is an already set topic."

		thisMonth = time.strftime("%m")
		thisDay = time.strftime("%d")
		key = "{}-{}".format(thisMonth, thisDay)
		topic.EVENTS = {key: ["Test Data."]}
		testSelf = self.TopicCatcher()
		topic.topicUpdated(testSelf, "", "#test", currTopic)

		self.assertEqual(testSelf.result, "")


if __name__ == "__main__":
	unittest.main()
