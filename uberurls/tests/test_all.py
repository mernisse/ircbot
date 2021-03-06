# -*- coding: UTF-8 -*-
''' test_all.py (c) 2018 Matthew J Ernisse <matt@going-flying.com>
All Rights Reserved.

Unit tests for the uberurls module.

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
import unittest

import core
import uberurls

class MockIrcBot(object):
	def __init__(self):
		self.result = []

	def msg(self, target, msg):
		self.result.append((target, msg))
		

class UberUrlsTestCase(unittest.TestCase):
	def setUp(self):
		self.bot = MockIrcBot()
		self.channel = "#test"
		self.user = "test!test.host"

	def testRedirectUrl(self):
		''' Should successfully follow HTTP redirects. '''
		expected = [(
			self.channel,
			'http://www.ub3rgeek.net/ [Matthew Ernisse]'
		)]
		msg = "http://www.ub3rgeek.net/"
		with self.assertRaises(core.StopCallBacks):
			uberurls.privmsg(self.bot, self.user, self.channel, msg)

		self.assertEqual(self.bot.result, expected)

	def testNonExistentUrl(self):
		''' Should not speak if the URL fails to load. '''
		expected = []
		msg = "http://foobar.baz"
		with self.assertRaises(Exception):
			uberurls.privmsg(self.bot, self.user, self.channel, msg)

		self.assertEqual(self.bot.result, expected)

	def testNoUrlMsg(self):
		''' Should not speak if there is no URL in the message. '''
		expected = []
		msg = ""
		uberurls.privmsg(self.bot, self.user, self.channel, msg)
		self.assertEqual(self.bot.result, expected)
	
