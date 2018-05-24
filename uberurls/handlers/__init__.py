# coding: utf-8
""" uberurls.handlers (c) 2013-2018 Matthew Ernisse <matt@going-flying.com>
All Rights Reserved.

Url processing helpers for the uberurls bot module.

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
"""
import requests
import sys

from . import *
from bs4 import BeautifulSoup
from botlogger import debug, err, log, logException
from html.parser import HTMLParser

__all__ = ["core", "itunes", "soundcloud", "youtube"]
__face__ = "( ͡° ͜ʖ ͡°)"


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

	if not response or not isinstance(response, requests.Response):
		err('processurl(): no module returned a valid response.')
		raise Exception('failed to load url')

	#
	# handle embedded encoding in the content-type field
	#
	mimetype = response.headers['content-type']
	if not mimetype.startswith('text/html'):
		return (url, mimetype)

	soup = BeautifulSoup(response.text, "lxml")
	title = load_title(url, soup)
	parser = HTMLParser()
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
