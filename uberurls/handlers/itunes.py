#!/usr/bin/python -tt
# coding: utf-8 
"""itunes.py (c) 2016 Matthew J Ernisse <matt@going-flying.com>

Sanitize functions for iTunes/Apple Music URLS

"""
import re
import sys
import urlparse

from botlogger import *

def load_title(url, soup):
	''' Load the iTunes item in a more obvious way.'''
	parsed_url = urlparse.urlparse(url)
	parsed_qs = urlparse.parse_qs(parsed_url.query)

	if not re.search(r'itun\.es|itunes\.apple\.com', parsed_url.netloc, re.I):
		return None

	if not 'i' in parsed_qs:
		log('itunes.load_title(): no item in url.')
		return None

	item = soup.find('tr', {'adam-id': parsed_qs['i']})
	if not item:
		err('itunes.load_title(): failed to find adam-id.')
		return None

	return "iTunes: %s - %s" % (
		item['preview-artist'], item['preview-title']
	)
