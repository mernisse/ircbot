# coding: utf-8
"""itunes.py (c) 2016 - 2018 Matthew J Ernisse <matt@going-flying.com>

Sanitize functions for iTunes/Apple Music URLS

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
import sys
import urllib.parse
from botlogger import err, log


def load_title(url, soup):
	''' Load the iTunes item in a more obvious way.'''
	parsed_url = urllib.parse.urlparse(url)
	parsed_qs = urllib.parse.parse_qs(parsed_url.query)

	if not re.search(r'itun\.es|itunes\.apple\.com', parsed_url.netloc, re.I):
		return None

	_id = None
	if 'i' in parsed_qs:
		_id = parsed_qs['i']
	else:
		_id = parsed_url.split("/")[-1]

	if not _id:
		err('itunes.load_title(): failed to find id.')
		return None

	item = soup.find('tr', {'adam-id': _id})
	if not item:
		print(soup)
		return None

	return "iTunes: %s - %s" % (
		item['preview-artist'], item['preview-title']
	)
