#!/usr/bin/python -tt
# coding: utf-8 
"""__init__.py - (c) 2014 Matthew John Ernisse <mernisse@ub3rgeek.net>

URL Database functions.

"""
import MySQLdb

import private # passwords and such are stored here to prevent leakage

SQL_HOST = private.UBERURLS_SQL_HOST
SQL_USER = private.UBERURLS_SQL_USER
SQL_PASS = private.UBERURLS_SQL_PASS
SQL_DB = private.UBERURLS_SQL_DB

def fetch_url_db(url):
	''' Check to see if a URL is in the database already '''

	global SQL_HOST, SQL_USER, SQL_PASS, SQL_DB

	sql = MySQLdb.connect(SQL_HOST, SQL_USER, SQL_PASS, SQL_DB)
	cursor = sql.cursor()
	cursor.execute("SELECT * FROM urls WHERE url = %s", (url))
	row = cursor.fetchone()

	if not row:
		cursor.execute("SELECT * FROM urls WHERE shorturl = %s", 
			(url))
		row = cursor.fetchone()

	sql.close()

	return row

def add_url_to_db(url, short, speaker):
	''' Add a new URL to the database '''

	global SQL_HOST, SQL_USER, SQL_PASS, SQL_DB

	count = 1

	sql = MySQLdb.connect(SQL_HOST, SQL_USER, SQL_PASS, SQL_DB)
	cursor = sql.cursor()
	cursor.execute("""INSERT INTO urls 
			(url, shorturl, user, count)
			VALUES(%s, %s, %s, %s)""", 
			(url, short, speaker, count)
	)
	sql.commit()
	sql.close()

def update_url_in_db(short, count):
	''' Update the URL in the DB '''

	global SQL_HOST, SQL_USER, SQL_PASS, SQL_DB
	count = int(count) + 1 

	sql = MySQLdb.connect(SQL_HOST, SQL_USER, SQL_PASS, SQL_DB)
	cursor = sql.cursor()
	cursor.execute("UPDATE urls SET count = %s WHERE shorturl = %s",
			(count, short)
	)
	sql.commit()
	sql.close()
