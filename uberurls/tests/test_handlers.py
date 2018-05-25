#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
''' test_handlers.py (c) 2018 Matthew J Ernisse <matt@going-flying.com>
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
import bs4
import requests
import sys
import unittest

sys.path.append("..")
sys.path.append("../..")

import handlers


def _getSoup(url):
	response = requests.get(url)
	return bs4.BeautifulSoup(response.text, "html5lib")

class CoreTestCase(unittest.TestCase):
	def testValidHttpsUrl(self):
		expected = ["https://www.example.com"]
		msg = "This is an example url https://www.example.com"
		result = handlers.core.detect_valid_urls(msg)
		self.assertEqual(expected, result)

	def testInvalidUrl(self):
		expected = []
		msg = "This is some example.com bs."
		result = handlers.core.detect_valid_urls(msg)
		self.assertEqual(expected, result)

	def testSchemelessUrl(self):
		expected = ["www.example.com"]
		msg = "What about www.example.com"
		result = handlers.core.detect_valid_urls(msg)
		self.assertEqual(expected, result)

	def testGetTitle(self):
		expected = "This is a Title"
		html = "<html><head><title>This is a Title       </title>"
		soup = bs4.BeautifulSoup(html, "html5lib")
		result = handlers.core.load_title("", soup)
		self.assertEqual(expected, result)


class iTunesHanderTestCase(unittest.TestCase):
	''' Module broken due to upstream changes. '''
	def testTrackUrl(self):
		expected = ""
		url = "https://itunes.apple.com/us/album/black-dog/580708175?i=580708177"

	def testAlbumUrl(self):
		url = "https://itunes.apple.com/us/album/led-zeppelin-iv-remastered/580708175"

	def testArtistUrl(self):
		url = "https://itunes.apple.com/us/artist/led-zeppelin/994656"


class SoundCloudHandlerTestCase(unittest.TestCase):
	def testTitleFromUrl(self):
		expected = "SoundCloud: A Letter To Alvin Defeer"
		url = "https://soundcloud.com/huttonorbital/a-letter-to-alivn-defeer"
		soup = _getSoup(url)
		result = handlers.soundcloud.load_title(url, soup)
		self.assertEqual(expected, result)


class SpotifyHandlerTestCase(unittest.TestCase):
	''' Module broken due to upstream changes. '''
	def testTrackUrl(self):
		url = "https://open.spotify.com/track/2qOm7ukLyHUXWyR4ZWLwxA"

	def testPlaylistUrl(self):
		url = "https://open.spotify.com/user/mlucchini/playlist/1ZNnRr9emCxsLP9zNY74wI"

	def testAlbumUrl(self):
		url = "https://open.spotify.com/album/5hchtJ6859VJ38c0bc5R0S"

	def testArtistUrl(self):
		url = "https://open.spotify.com/artist/2UwJRAgSOi1zcLkvUNc8XL"


class YoutubeHandlerTestCase(unittest.TestCase):
	def testRegularUrl(self):
		expected = "https://youtube.com/watch?v=eJSa4reIYkU"
		url = "https://www.youtube.com/watch?v=eJSa4reIYkU"
		result = handlers.youtube.sanitize_url(url)
		self.assertEqual(expected, result)

	def testShortenedUrl(self):
		expected = "https://youtube.com/watch?v=eJSa4reIYkU"
		url = "https://youtu.be/eJSa4reIYkU"
		result = handlers.youtube.sanitize_url(url)
		self.assertEqual(expected, result)

	def testHttpUrl(self):
		expected = "https://youtube.com/watch?v=eJSa4reIYkU"
		url = "http://www.youtube.com/watch?v=eJSa4reIYkU"
		result = handlers.youtube.sanitize_url(url)
		self.assertEqual(expected, result)

	def testTimeStampedUrl(self):
		expected = "https://youtube.com/watch?v=eJSa4reIYkU&t=3m45s"
		url = "https://youtu.be/eJSa4reIYkU?t=3m45s"
		result = handlers.youtube.sanitize_url(url)
		self.assertEqual(expected, result)

	def testPlaylistUrl(self):
		expected = "https://youtube.com/watch?v=ftJ17Cp6itw&list=PLvgS71fU12Mbx-w18Chu_Sg9v6loipEFO"
		url = "https://www.youtube.com/watch?v=ftJ17Cp6itw&list=PLvgS71fU12Mbx-w18Chu_Sg9v6loipEFO"
		result = handlers.youtube.sanitize_url(url)
		self.assertEqual(expected, result)

	def testPlaylistWithTimeUrl(self):
		expected = "https://youtube.com/watch?v=ftJ17Cp6itw&t=1m10s&list=PLvgS71fU12Mbx-w18Chu_Sg9v6loipEFO"
		url = "https://www.youtube.com/watch?v=ftJ17Cp6itw&list=PLvgS71fU12Mbx-w18Chu_Sg9v6loipEFO&t=1m10s"
		result = handlers.youtube.sanitize_url(url)
		self.assertEqual(expected, result)

	def testStripsTrackingFromUrl(self):
		expected = "https://youtube.com/watch?v=eJSa4reIYkU"
		url = "http://www.youtube.com/watch?v=eJSa4reIYkU&utm_source=random"
		result = handlers.youtube.sanitize_url(url)
		self.assertEqual(expected, result)


if __name__ == "__main__":
	unittest.main()
