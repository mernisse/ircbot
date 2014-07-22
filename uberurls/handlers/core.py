#!/usr/bin/python -tt
# coding: utf-8 
"""core.py (c) 2014 Matthew J Ernisse <mernisse@ub3rgeek.net>

Base handler for urls.

"""
import cgi
import re
import sys
import urllib
import urllib2
import urlparse

from bs4 import BeautifulSoup

import youtube

URLLIB_RESPONSE=None

def processurl(speaker, url):
	''' try to fetch a url from the interwebs.  store some info about
	who mentioned it in the database (keeping track of mention counts)
	along with some meta information from the url (content of the html
	title tag if it is present or the mime-type if it is not a text/html
	page).

	''' 

	global URLLIB_RESPONSE

	try:
		parsed = urlparse.urlparse(url)
		query = urlparse.parse_qs(parsed.query)

		request = urllib2.Request(url)
		request.add_header('User-Agent', 'uberurls/1.0 (python)')
		URLLIB_RESPONSE = urllib2.urlopen(request)

	except urllib2.URLError, e:
		return (url, "%s is dead %s ╯(°□°)╯ ︵┻━┻ " % (url, e.reason))

	#
	# Clean up urls here
	#
	url = sanitize_url(url)
	url = youtube.sanitize_url(url)

	#
	# handle embedded encoding in the content-type field
	#
	mimetype = URLLIB_RESPONSE.info()['content-type']
	if not mimetype.startswith('text/html'):
		return (url, mimetype)

	#
	# fetch titles here
	#
	title = load_title()

	return (url, title)


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

def load_title():
	''' Return the title of the page. '''

	global URLLIB_RESPONSE

	try:
		soup = BeautifulSoup(URLLIB_RESPONSE)
		title = cgi.escape(soup.title.string)
		title = title.encode('ascii', 'xmlcharrefreplace')

	except Exception, e:
		sys.stderr.write('core.load_title(): %s\n' % (str(e)))
		return ''

	return title
