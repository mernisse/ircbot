# coding: utf-8
'''gemini.py (c) 2021 Matthew J Ernisse <matt@going-flying.com>

Base handler for gemini:// urls.

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
import re
import ignition
from botlogger import log, logException
from urllib.parse import urlparse


def detect_valid_urls(s):
	''' Return a list of Gemini URLs extracted from a string. '''
	r = re.compile(r'((?:gemini://|gemini\.)[-\w\d+&@#/\\%=~_|$?!:;,.]*[-\w\d+&@#/\\%=~_|$])', re.I)

	matches = r.findall(s)
	if not matches:
		return []

	ret = []
	for match in matches:
		parsed = urlparse(match)
		if not parsed.scheme:
			match = f'gemini://{match}'

		ret.append(match)

	return ret


def processurl(url):
	''' try to fetch a url from the smol interwebs. '''
	parsed = urlparse(url)
	if parsed.scheme is not 'gemini' \
		and not parsed.netloc.startswith('gemini'):
			return None

	response = ignition.request(url)
	if not response.success():
		log(f'There was an error fetching {url}')
		raise Exception('Error fetching {url}')

	log(f'gemini.processurl(): loaded {url}')
	return url


def load_title(url, _):
	''' Return the https proxy url for the page. '''
	parsed = urlparse(url)
	if parsed.scheme is not 'gemini' \
		and not parsed.netloc.startswith('gemini'):
		return None

	return f'https://proxy.vulpes.one/gemini/{parsed.netloc}{parsed.path}'
