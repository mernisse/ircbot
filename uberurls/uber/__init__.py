# coding: utf-8 
"""uber/__init__.py - (c) 2014 - 2018 Matthew Ernisse <matt@going-flying.com>
All Rights Reserved.

Handle shortening of urls with uber.hk

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
import core
import json
import requests
import urllib.parse

from botlogger import *

def shorten(url):
	''' shorten the given url using the super excellent uber.hk
	url shortening service!

	'''
	logger.debug('uber.hk - got url %s' % url)
	parsed = urllib.parse.urlparse(url)
	if parsed.netloc == 'uber.hk':
		return url

	try:
		quoted_url = urllib.parse.quote(url)
		api_key = config.getStr("api_key")
		post_url = config.getStr("api_url")

		resp = requests.post(post_url.format(api_key, quoted_url))
		data = resp.json()
		logger.debug('uber.hk - API reply %s' % str(data))
		resp.raise_for_status()
		return 'http://uber.hk/%s' % data['code']

	except Exception as e:
		logException(e)
		return url

config = core.config.getChildren("uberurls")
