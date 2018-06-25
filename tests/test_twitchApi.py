#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
'''test_twitchApi.py (c) 2018 Matthew J Ernisse <matt@going-flying.com>
All Rights Reserved.

Unit tests for the Twitch API module

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
import requests
import sys
import time
import unittest
from unittest import mock

import twitchApi

sys.path.append("tests")
import utils


class TwitchApiStreamTests(unittest.TestCase):
	def setUp(self):
		self.twitchApi = mock.create_autospec(twitchApi.TwitchClient)
		self.stream = twitchApi.Stream(self.twitchApi, "test1")

		self.json = utils.JSON_REPLIES["getStreamingStatus"]
		self.twitchApi.getStreamingStatus.return_value = \
			self.json["data"]
		self.twitchApi.getUserId.return_value = "1234567890"

	def testStreamLazyLoad(self):
		""" The API should not load unless properties are needed. """
		self.assertFalse(self.twitchApi.getStreamingStatus.called)
		self.assertFalse(self.twitchApi.getUserId.called)

	def testStreamRefresh(self):
		""" The API should refresh if needed."""
		self.assertEqual(self.stream.userId, "1234567890")
		self.assertEqual(
			1,
			 self.twitchApi.getUserId.call_count
		)

	def testStreamRefreshException(self):
		""" The refresh should not raise an exception, or destroy
		already loaded data.
		"""
		self.assertTrue(self.stream.live)
		self.stream._lastChecked = 0
		self.twitchApi.getStreamingStatus.side_effect = Exception("")
		self.assertTrue(self.stream.live)

	def testStreamWontRefresh(self):
		""" We should only refresh if needed."""
		self.assertTrue(self.stream.live)
		self.assertEqual(
			1,
			 self.twitchApi.getStreamingStatus.call_count
		)

		self.assertTrue(self.stream.live)
		self.assertEqual(
			1,
			self.twitchApi.getStreamingStatus.call_count
		)

	def testStreamUptime(self):
		""" Test the uptime prettyPrint """
		now = time.time()
		self.stream._lastChecked = now
		self.stream.started_at = now - 694925
		self.stream._live = True
		self.assertEqual(
			"1 wk, 1 day, 1 hour, 2:05",
			self.stream.uptime
		)

		self.stream.started_at = now - 180000
		self.assertEqual(
			'2 days, 2 hours, 0:00',
			self.stream.uptime
		)

		self.stream.started_at = now - 123
		self.assertEqual(
			'2 minutes, 3 seconds',
			self.stream.uptime
		)

		self.stream.started_at = now - 63
		self.assertEqual(
			'1 minute, 3 seconds',
			self.stream.uptime
		)

		self.stream.started_at = now - 3
		self.assertEqual(
			'3 seconds',
			self.stream.uptime
		)

		self.stream._live = False
		self.assertEqual(
			'No current stream.',
			self.stream.uptime
		)
		
	def testStreamUserIdException(self):
		""" userId should be None if API failure... """
		self.twitchApi.getUserId.side_effect = Exception("")
		self.assertEqual(None, self.stream.userId)

	def testTwitchApiDateConversion(self):
		api = twitchApi.TwitchClient('')
		epoch = "1970-01-01T00:00:00Z"
		expected = 0
		self.assertEqual(
			expected,
			api.dateStringToSecs(epoch)
		)

		epoch = "1981-09-18T04:37:00Z"
		expected = 369635820
		self.assertEqual(
			expected,
			api.dateStringToSecs(epoch)
		)

		epoch = "2038-01-19T03:14:07Z"
		expected = 2**31-1
		self.assertEqual(
			expected,
			api.dateStringToSecs(epoch)
		)


class TwitchApiClientTests(unittest.TestCase):
	def setUp(self):
		self.api = twitchApi.TwitchClient('')
		self.mock_response = mock.Mock()

	@mock.patch('twitchApi.requests.get')
	def testGetUserId(self, mock_requests):
		mock_requests.return_value = self.mock_response
		self.mock_response.json.return_value = utils.JSON_REPLIES["getUserId"]
		self.assertEqual("1234567890", self.api.getUserId("test1"))

	@mock.patch('twitchApi.requests.get')
	def testFailedUserId(self, mock_requests):
		self.mock_response.json.return_value = None
		mock_requests.return_value = self.mock_response
		with self.assertRaises(ValueError):
			userId = self.api.getUserId("test2")

	@mock.patch('twitchApi.requests.get')
	def testGetStreamingStatus(self, mock_requests):
		mock_requests.return_value = self.mock_response
		self.mock_response.json.return_value = utils.JSON_REPLIES["getStreamingStatus"]

		self.assertEqual(
			"Test Stream",
			self.api.getStreamingStatus("test1")[0]["title"]
		)
