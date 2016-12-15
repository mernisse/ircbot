#!/usr/bin/python -tt
# coding: utf-8 
"""core.py (c) 2014-2016 Matthew J Ernisse <matt@going-flying.com>

Base handler for urls.

"""
import cookielib
import cgi
import re
import sys
import urllib
import urllib2
import urlparse

from botlogger import *

def processurl(url):
	''' try to fetch a url from the interwebs. ''' 

	try:
		# some websites do a redirect dance that requires cookies.
		jar = cookielib.CookieJar()
		opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(jar))
		urllib2.install_opener(opener)

		parsed = urlparse.urlparse(url)
		query = urlparse.parse_qs(parsed.query)

		request = urllib2.Request(url)
		request.add_header('User-Agent', 'uberurls/2.0 (python)')
		response = urllib2.urlopen(request)

		# Don't keep cookies beyond what is required to service
		# the initial request.
		jar.clear()

	except urllib2.URLError, e:
		err('core.processurl(): failed to load %s: %s' % (url, e.reason))
		return "%s is dead %s ╯(°□°)╯ ︵┻━┻ " % (url, e.reason)

	log('core.processurl(): loaded %s' % (url))
	return response

#
# Helpers
#
def detect_valid_urls(s):
	''' Return a list of URLs extracted from a string. '''

	r = re.compile('((?:https?://|www\.|ftp\.)[-\w\d+&@#/\\%=~_|$?!:;,.]*[-\w\d+&@#/\\%=~_|$])', re.I)

	try:
		matches = r.findall(s)
		if not matches:
			return []

		return matches

	except Exception, e:
		return []


def sanitize_url(url):
	''' Fetch a url and return the ultimate destination to defeat all
	the url shorteners link trackers.

	'''

	global URLLIB_RESPONSE

	try:
		if not URLLIB_RESPONSE:
			return url

		canonical_url = URLLIB_RESPONSE.geturl()
		if url != canonical_url:
			return canonical_url

		return url

	except Exception, e:
		return url

def load_title(url, soup):
	''' Return the title of the page. '''

	try:
		title = cgi.escape(soup.title.string)
		title = title.encode('ascii', 'xmlcharrefreplace')
		title = title.strip()

	except Exception, e:
		err('core.load_title(): error: %s\n' % (str(e)))
		return None

	return title
