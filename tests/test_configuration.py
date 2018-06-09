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

import core

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
