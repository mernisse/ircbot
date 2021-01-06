# coding: utf-8
""" uberurls.handlers (c) 2013-2021 Matthew Ernisse <matt@going-flying.com>
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
import html
import requests
import sys

from . import core, gemini, soundcloud, youtube
from bs4 import BeautifulSoup
from botlogger import debug, err, log, logException
from html.parser import HTMLParser

__all__ = ["core", "gemini", "soundcloud", "youtube"]
__face__ = "( ͡° ͜ʖ ͡°)"


def detect_valid_urls(s):
	''' Dispatch a privmsg to any module that cares to see if it can
	find a url it wants in there.

	Return a list of tuples with the module and the url.
	'''

	found = []
	for mod in __all__:
		mod = ".".join([__name__, mod])

		if not getattr(sys.modules[mod], 'detect_valid_urls', None):
			continue

		poised = sys.modules[mod].detect_valid_urls(s)
		if not poised:
			continue

		for url in poised:
			found.append((mod, url))

	return found


def processurl(mod_url):
	'''  Expects a tuple of (module name, url) as returned by
	detect_valid_urls.  Call the submodule's processurl function.

	If that returns a requests.Reponse it will be loaded into
	BeautifulSoup prior to passing to load_title().
	'''
	poised = None
	responder = None
	response = None
	mod = mod_url[0]
	url = sanitize_url(mod_url[1])

	if not getattr(sys.modules[mod], 'processurl', None):
		err('processurl(): no module returned a valid response.')
		raise Exception('failed to load url')

	response = sys.modules[mod].processurl(url)
	if not response:
		return

	if not isinstance(response, requests.Response):
		title = load_title(url, response)

	elif not response.headers.get('content-type').startswith('text/html'):
		title = response.headers.get('content-type')

	else:
		soup = BeautifulSoup(response.text, "lxml")
		title = load_title(url, soup)
		title = html.unescape(title)

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
	Call all submodules load_title functions.  The called function should
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
			log(f'load_title(): {mod} returned {poised}')
			title = poised

	if title:
		return title

	err('load_title(): no modules cared to load the title.')
	return 'Unknown'
