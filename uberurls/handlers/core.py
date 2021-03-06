# coding: utf-8
"""core.py (c) 2014-2021 Matthew J Ernisse <matt@going-flying.com>

Base handler for urls.

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
import re
import requests
from botlogger import log, logException
from urllib.parse import urlparse


def detect_valid_urls(s):
	''' Return a list of URLs extracted from a string.  '''
	r = re.compile('((?:https?://|www\.|ftp\.)[-\w\d+&@#/\\%=~_|$?!:;,.]*[-\w\d+&@#/\\%=~_|$])', re.I)

	matches = r.findall(s)
	if not matches:
		return []

	ret = []
	for match in matches:
		parsed = urlparse(match)
		if not parsed.scheme:
			match = f'https://{match}'

		ret.append(match)

	return ret


def load_title(url, soup):
	''' Return the title of the page.  In case of error, return what we
	were able to convert.'''
	try:
		return soup.title.text.strip()
	except Exception as e:
		return None


def processurl(url):
	''' try to fetch a url from the interwebs. '''
	# Looks like streams respond with 501 for HEAD, at least
	# Akamai ones do, so try that first just to try to guard
	# against the bot wedging in here...
	response = requests.head(
		url,
		headers={"User-Agent": "uberurls/3.0 (python)"},
		timeout=2
	)
	response.raise_for_status()

	response = requests.get(
		url,
		headers={"User-Agent": "uberurls/3.0 (python)"},
		timeout=2
	)
	response.raise_for_status()

	log(f'core.processurl(): loaded {url}')
	return response

