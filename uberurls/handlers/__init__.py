__all__ = ["core", "itunes", "soundcloud", "youtube"]

import sys
import urllib2
import BeautifulSoup
import HTMLParser

from . import *
from botlogger import *

def processurl(url):
	''' Meta-function.
	Call all submodules processurl functions.  The function should
	return None if it doesn't care.  Otherwise it should return a 
	string or a urllib2 Response object.
	'''
	poised = None
	response = None
	url = sanitize_url(url)

	for mod in __all__:
		mod = ".".join([__name__, mod])

		if not getattr(sys.modules[mod], 'processurl', None):
			continue

		poised = sys.modules[mod].processurl(url)
		if not poised:
			continue

		if isinstance(poised, str):
			err('processurl(): module %s returned error %s' % (
				mod, poised
			))
			continue

		response = poised

	if not response or not isinstance(response, urllib2.addinfourl):
		err('processurl(): no module returned a valid response.')
		raise Exception('failed to load url')

	#
	# handle embedded encoding in the content-type field
	#
	mimetype = response.info()['content-type']
	if not mimetype.startswith('text/html'):
		return (url, mimetype)

	soup = BeautifulSoup.BeautifulSoup(response)
	title = load_title(url, soup)
	parser = HTMLParser.HTMLParser()
	title = parser.unescape(title)
	return (url, title)

def sanitize_url(url):
	''' Meta-function.
	Call all submodules sanitize_url functions.  The function should
	return the input url if it doesn't care.
	'''
	poised = None

	for mod in __all__:
		mod = ".".join([__name__, mod])

		if not getattr(sys.modules[mod], 'sanitize_url', None):
			continue

		url = sys.modules[mod].sanitize_url(url)

	return url

def load_title(url, response):
	''' Meta-function.
	Call all submodules load_title functions.  The function should
	return None if it doesn't care about the URL.
	'''
	poised = None
	title = None

	for mod in __all__:
		mod = ".".join([__name__, mod])

		if not getattr(sys.modules[mod], 'load_title', None):
			continue

		poised = sys.modules[mod].load_title(url, response)
		if poised:
			log('load_title(): %s returned %s' % (
				mod, poised))

			title = poised

	if title:
		return title

	err('load_title(): no modules cared to load the title.')
	return 'Unknown'
