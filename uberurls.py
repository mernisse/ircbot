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
	log('processing url %s from %s' % (speaker, url))
	try:
		request = urllib2.Request(url)
		request.add_header('User-Agent', 'uberurls ircbot/python')
		fp = urllib2.urlopen(request)
	except urllib2.URLError, e:
		log("uberurls - could not open %s, %s" % (url, e.reason))
		return "%s is dead %s" % (url, e.reason)

	#
	# Clean up urls here
	#

	try:
		sql = MySQLdb.connect(SQL_HOST, SQL_USER, SQL_PASS, SQL_DB)
		cursor = sql.cursor()
		cursor.execute("SELECT * FROM urls WHERE url = %s", (url))
		row = cursor.fetchone()
	except Exception, e:
		log('uberurls - db error: %s' % str(e))
		return '[uberurls - DB ERROR]'

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
			log('uberurls - db error on INSERT: %s' % str(e))
			return '[uberurls - DB ERROR]'

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
			log('could not update URL in DB: %s' % str(e))
			return '[uberurls - DB ERROR]'

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
				log('could not reshorten URL: %s' % str(e))
				return '[uberurls - DB ERROR]'

	#
	# handle embedded encoding in the content-type field
	#
	if not fp.info()['content-type'].startswith('text/html'):
		return "%s [%s, %s mentioned %ix]" % (
			shorturl,
			fp.info()['content-type'],
			original,
			count
		)

	try:
		soup = BeautifulSoup(fp)
		title = cgi.escape(soup.title.string)
		title = title.encode('ascii', 'xmlcharrefreplace')
	except Exception, e:
		log("uberurls - error getting title %s" % str(e))
		return "%s [%s mentioned %ix]" % (
			shorturl,
			original,
			count
		)

	return "%s [%s, %s mentioned %ix]" % (
		shorturl,
		title,
		original,
		count
	)

def fetchshorturl(url):
	#
	# Do not shorten already shortened urls.
	#
	parsed = urlparse.urlparse(url)
	if parsed.netloc.startswith('uber.hk'):
		return url

	try:
		qurl = urllib.quote(url)
		fp = urllib2.urlopen("http://uber.hk/api/add?u=%s" % (qurl))
		return "".join(fp.readlines()).strip()
	except Exception, e:
		log('uberurls - failed to shorten %s, %s' % (
			url,
			str(e)
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
				err('error doing url stuff')
				return

			self.msg(channel, msg, only=True)

	except Exception, e:
		err('uberurls - ERROR: %s' % (
			str(e)
		))

core.register_module(__name__)
