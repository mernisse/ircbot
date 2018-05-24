#!/usr/bin/env python3
import bs4
import requests
import sys
import unittest

sys.path.append("..")
sys.path.append("../..")

import handlers


def _getSoup(url):
	response = requests.get(url)
	return bs4.BeautifulSoup(response.text, "lxml")

class coreTestCase(unittest.TestCase):
	def testValidHttpsUrl(self):
		expected = ["https://www.example.com"]
		msg = "This is an example url https://www.example.com"
		result = handlers.core.detect_valid_urls(msg)
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
