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

import ascii
import core

sys.path.append("tests")
import utils


class AsciiTests(unittest.TestCase):
	fieldLol = [
		"l>      l>\n",
		"l       l\n",
		"l   ()  l\n",
		"l       l\n",
		"loooooool\n",
		"    l\n",
		"    l\n",
		" ",
		"FIELD LOL\n",
	]

	def setUp(self):
		self.bot = utils.StubIrcRobot()

	def testAsciiArt(self):
		with self.assertRaises(core.StopCallBacks):
			ascii.privmsg(
				self.bot,
				"test",
				"#test",
				"testbotnick: ascii fieldlol"
			)

		for i in range(0, len(self.fieldLol)):
			self.assertEqual(self.bot.messages[i][1], self.fieldLol[i])

	def testIgnoresJunkChars(self):
		ascii.privmsg(self.bot, "test", "#test", "ascii ../../README.md")
		self.assertEqual(self.bot.messages, [])

	def testIgnoresNonDirected(self):
		ascii.privmsg(self.bot, "test", "#test", "ascii fieldlol")
		self.assertEqual(self.bot.messages, [])

	def testRejectsNonExistant(self):
		with self.assertRaises(core.StopCallBacks):
			ascii.privmsg(
				self.bot,
				"test",
				"#test",
				"testbotnick: ascii nonExistant"
			)
		self.assertEqual(
			self.bot.messages,
			[("#test", "I do not know of what you speak.")]
		)
