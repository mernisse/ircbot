# coding: utf-8
"""youtube.py (c) 2014 - 2018 Matthew J Ernisse <matt@going-flying.com>

Sanitize functions for Youtube URLs

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
import urllib.parse


def sanitize_url(url):
	''' cleanup youtube links, also strip the stupid link tracking BS
	and always make use of HTTPS.
	'''
	parsed_url = urllib.parse.urlparse(url)
	parsed_qs = urllib.parse.parse_qs(parsed_url.query)

	if not re.search(r'youtube\.com|youtu\.be', parsed_url.netloc, re.I):
		return url

	canonical_qs = ''
	canonical_url = 'https://youtube.com/watch?v='
	if 't' in parsed_qs:
		canonical_qs += '&t=' + parsed_qs['t'][0]

	if 'list' in parsed_qs:
		canonical_qs += '&list=' + parsed_qs['list'][0]

	if 'v' in parsed_qs:
		canonical_url += "%s%s" % (
			parsed_qs['v'][0],
			canonical_qs)

	elif 'youtu.be' in parsed_url.netloc:
		canonical_url += '%s%s' % (
			parsed_url.path[1:],
			canonical_qs)

	return canonical_url
