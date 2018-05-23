"""__init__.py - (c) 2014 - 2018 Matthew J. Ernisse <matt@going-flying.com>

URL Database functions.

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
import MySQLdb

from botlogger import *

config = core.config.getChildren("uberurls")
SQL_HOST = config.getStr("sql_host")
SQL_USER = config.getStr("sql_user")
SQL_PASS = config.getStr("sql_pass")
SQL_DB = config.getStr("sql_db")

def fetch_url_db(url):
	''' Check to see if a URL is in the database already '''

	global SQL_HOST, SQL_USER, SQL_PASS, SQL_DB

	sql = MySQLdb.connect(SQL_HOST, SQL_USER, SQL_PASS, SQL_DB)
	cursor = sql.cursor()
	cursor.execute("SELECT * FROM urls WHERE url = %s", (url,))
	row = cursor.fetchone()

	if not row:
		cursor.execute("SELECT * FROM urls WHERE shorturl = %s", 
			(url,))
		row = cursor.fetchone()

	sql.close()

	return row

def add_url_to_db(url, short, speaker):
	''' Add a new URL to the database '''

	global SQL_HOST, SQL_USER, SQL_PASS, SQL_DB

	count = 1

	try:
		sql = MySQLdb.connect(SQL_HOST, SQL_USER, SQL_PASS, SQL_DB)
		cursor = sql.cursor()
		cursor.execute("""INSERT INTO urls 
				(url, shorturl, user, count)
				VALUES(%s, %s, %s, %s)""", 
				(url, short, speaker, count)
		)
		sql.commit()
		sql.close()
	except Exception as e:
		logException(e)
		raise

def update_url_in_db(short, count):
	''' Update the URL in the DB '''

	global SQL_HOST, SQL_USER, SQL_PASS, SQL_DB
	count = int(count) + 1 

	try:
		sql = MySQLdb.connect(SQL_HOST, SQL_USER, SQL_PASS, SQL_DB)
		cursor = sql.cursor()
		cursor.execute("UPDATE urls SET count = %s WHERE shorturl = %s",
				(count, short)
		)
		sql.commit()
		sql.close()
	except Exception as e:
		logException(e)
		raise
