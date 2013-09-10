#!/usr/bin/python -tt
"""uberurls.py - (c) 2013 Matthew John Ernisse <mernisse@ub3rgeek.net>

Catch, log, and shorten urls.  Uses uber.hk because that is mine.

"""
import cgi
import core
import os
import re
import sys
import urllib
import urllib2
import urlparse

from botlogger import *
from bs4 import BeautifulSoup

import MySQLdb

import private # passwords and such are stored here to prevent leakage

SQL_HOST = private.UBERURLS_SQL_HOST
SQL_USER = private.UBERURLS_SQL_USER
SQL_PASS = private.UBERURLS_SQL_PASS
SQL_DB = private.UBERURLS_SQL_DB

def processurl(speaker, url):
	''' try to fetch a url from the interwebs.  store some info about
	who mentioned it in the database (keeping track of mention counts)
	along with some meta information from the url (content of the html
	title tag if it is present or the mime-type if it is not a text/html
	page).

	''' 
	log('processing url %s from %s' % (speaker, url))
	try:
		request = urllib2.Request(url)
		request.add_header('User-Agent', 'uberurls ircbot/python')
		fp = urllib2.urlopen(request)

	except urllib2.URLError, e:
		err("uberurls - could not urlopen %s, %s" % (url, e.reason))
		return "%s is dead %s" % (url, e.reason)

	#
	# Clean up urls here
	#

	# sanitize youtube links.
	if re.search(r'youtube\.com|youtu\.be', url):
		parsed = urlparse.urlparse(url)
		query = urlparse.parse_qs(parsed.query)
		canonical_qs = ''
		canonical_url = ''
		if 't' in query:
			canonical_qs += '&t=' + str(query['t'][0])

		if 'list' in query:
			canonical_qs += '&list=' + str(query['list'][0])

		if 'v' in query:
			canonical_url += 'https://youtube.com/watch?v=' + str(query['v'][0])
			canonical_url += canonical_qs

		elif 'youtu.be' in parsed.netloc:
			canonical_url += 'https://youtube.com/watch?v=' + str(parsed.path[1:])
			canonical_url += canonical_qs

		else:
			canonical_url = url
			canonical_url = re.sub('^http', 'https', url)

		url = canonical_url

	try:
		sql = MySQLdb.connect(SQL_HOST, SQL_USER, SQL_PASS, SQL_DB)
		cursor = sql.cursor()
		cursor.execute("SELECT * FROM urls WHERE url = %s", (url))
		row = cursor.fetchone()

	except Exception, e:
		err('uberurls - SELECT error: %s' % str(e))
		return

	if not row:
		shorturl = fetchshorturl(url)		

		count = 1
		original = speaker

		try:
			cursor.execute("""INSERT INTO urls 
				(url, shorturl, user, count)
				VALUES(%s, %s, %s, %s)""", 
				(url, shorturl, original, count)
			)
			sql.commit()
		
		except Exception, e:
			err('uberurls - INSERT error: %s' % str(e))
			return

	else:
		shorturl = row[2]
		original = row[3]
		count = int(row[4]) + 1 
		log('got %s by %s (%ix)' % (shorturl, original, count)) 

		try:
			cursor.execute("UPDATE urls SET count = %s WHERE url = %s",
				(count, url)
			)
			sql.commit()

		except Exception, e:
			err('uberurls - UPDATE error: %s' % str(e))
			return

		#
		# fetchshorturl() will return the original row if it cannot
		# shorten the url for some reason, so detect that and try to
		# re-shorten that url.
		#
		if not shorurl.startswith('http://uber.hk'):
			shorturl = fetchshorturl(url)
			try:
				cursor.execute("UPDATE urls SET shorturl = %s",
					(shorturl,))
				sql.commit()
				sql.close()

			except Exception, e:
				err('uberurls - could not reshorten URL: %s' % str(e))
				return
	#
	# handle embedded encoding in the content-type field
	#
	if not fp.info()['content-type'].startswith('text/html'):
		return "%s [%s, %s mentioned %ix]" % (
			shorturl, fp.info()['content-type'], original, count
		)

	try:
		soup = BeautifulSoup(fp)
		title = cgi.escape(soup.title.string)
		title = title.encode('ascii', 'xmlcharrefreplace')

	except Exception, e:
		err("uberurls - error getting title %s" % str(e))
		return "%s [%s mentioned %ix]" % (
			shorturl, original, count
		)

	return "%s [%s, %s mentioned %ix]" % (
		shorturl, title, original, count
	)

def fetchshorturl(url):
	''' shorten the given url using the super excellent uber.hk
	url shortening service!

	'''
	parsed = urlparse.urlparse(url)
	if parsed.netloc.startswith('uber.hk'):
		return url

	try:
		qurl = urllib.quote(url)
		fp = urllib2.urlopen("http://uber.hk/api/add?u=%s" % (qurl))
		return "".join(fp.readlines()).strip()

	except Exception, e:
		err('uberurls - failed to shorten %s, %s' % (
			url, str(e)
		))
		return url

def privmsg(self, user, channel, msg):
	speaker = user.split('!', 1)[0]

	#
	# look for a url in the incoming text
	#
	try:
		matches = re.findall(r'(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)', msg)
		if not matches:
			return None

		for url in matches:
			msg = processurl(speaker, url)
			if not msg:
				return

			self.msg(channel, msg, only=True)

	except core.StopCallBacks:
		raise

	except Exception, e:
		err('uberurls - Uncaught Error: %s' % (str(e)))

core.register_module(__name__)
