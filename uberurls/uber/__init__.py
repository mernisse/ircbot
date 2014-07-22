#!/usr/bin/python -tt
# coding: utf-8 
"""uber/__init__.py - (c) 2014 Matthew John Ernisse <mernisse@ub3rgeek.net>

Handle shortening of urls with uber.hk

"""
import urllib
import urllib2
import urlparse

def shorten(url):
	''' shorten the given url using the super excellent uber.hk
	url shortening service!

	'''
	parsed = urlparse.urlparse(url)
	if parsed.netloc == 'uber.hk':
		return url

	try:
		qurl = urllib.quote(url)
		resp = urllib2.urlopen("http://uber.hk/api/add?u=%s" % (qurl))
		return "".join(resp.readlines()).strip()

	except Exception, e:
		return url
