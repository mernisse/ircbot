#!/usr/bin/python -tt
# coding: utf-8 
"""youtube.py (c) 2014 Matthew J Ernisse <mernisse@ub3rgeek.net>

Sanitize functions for Youtube URLs

"""
import re
import urlparse

def sanitize_url(url):
	''' cleanup youtube links, also strip the stupid link tracking BS
	and always make use of HTTPS.

	'''

	parsed_url = urlparse.urlparse(url)
	parsed_qs = urlparse.parse_qs(parsed_url.query)

	if not re.search(r'youtube\.com|youtu\.be', parsed_url.netloc, re.I):
		return url

	canonical_qs = ''
	canonical_url = 'https://youtube.com/watch?v='
	if 't' in parsed_qs:
		canonical_qs += '&t=' + str(parsed_qs['t'][0])

	if 'list' in parsed_qs:
		canonical_qs += '&list=' + str(parsed_qs['list'][0])

	if 'v' in parsed_qs:
		canonical_url += "%s%s" % (
			str(parsed_qs['v'][0]),
			canonical_qs)

	elif 'youtu.be' in parsed_url.netloc:
		canonical_url = 's%s' % (
			str(parsed_url.path[1:]),
			canonical_qs)

	else:
		canonical_url = url
		canonical_url = re.sub('^http:', 'https:', url)

	return canonical_url
