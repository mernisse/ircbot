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

import nethack

sys.path.append("tests")
import utils


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
