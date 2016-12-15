#!/usr/bin/python -tt
# coding: utf-8 
"""soundcloud.py (c) 2016 Matthew J Ernisse <matt@going-flying.com>

Sanitize functions for SoundCloud URLs

"""
import re
import sys
import urlparse
import HTMLParser

def load_title(url, soup):
	''' Load the SoundCloud item in a more obvious way.'''

	parsed_url = urlparse.urlparse(url)

	if not re.search(r'soundcloud\.com', parsed_url.netloc, re.I):
		return None

	item = soup.find('h1', {'itemprop': 'name'})
	if not item:
		return None

	item = item.find('a', {'itemprop': 'url'}).text
	return "SoundCloud: %s" % (item)
