#!/usr/bin/python -tt
''' idler.py (c) 2013 Matthew J Ernisse <mernisse@ub3rgeek.net>

Implement an idle tracker - this is NOT IdleRPG like in that it
does not penalize users for talking, it just keeps track of idle
time.

'''

import core
import time
import private
import re
import MySQLdb

from botlogger import *

ACTIVE_CHANNELS = ['#adultflirt', '#test'] # list of channels to care about.
IDLERS = {}  # players
MESSAGES = {}
TIMER = 3600 # base timer for each level
SCALER = 1.4 # exponent to scale the next level by

SQL_HOST = private.IDLERS_SQL_HOST
SQL_USER = private.IDLERS_SQL_USER
SQL_PASS = private.IDLERS_SQL_PASS
SQL_DB = private.IDLERS_SQL_DB

def db_get(nick, channel):
	''' get a player from the DB '''
	global SQL_HOST, SQL_USER, SQL_PASS, SQL_DB
	try:
		sql = MySQLdb.connect(SQL_HOST, SQL_USER, SQL_PASS, SQL_DB)
		cursor = sql.cursor()
		cursor.execute('''SELECT * FROM players 
			WHERE nick = %s
			AND channel = %s''',
			(nick, channel,))
		row = cursor.fetchone()		
		sql.close()

	except Exception, e:
		# I am not sure what to do here yet, I don't want
		# the bot to dump someone to level one if the DB
		# is down...
		err('idler - SELECT error: %s' % str(e))
		raise

	if not row:
		player = {
			'nick': nick,
			'channel': channel,
			'level': 1,
			'next_level': TIMER,
			'progress': 0.0,
		}
		return player

	# id | nick | channel | level | login | last_spoken | next_level | progress
	player = {}
	player['level'] = int(row[3])
	player['next_level'] = float(row[6])
	player['progress'] = float(row[7])

	return player

def db_set(player):
	''' update a player in the db '''
	global SQL_HOST, SQL_USER, SQL_PASS, SQL_DB
	try:
		sql = MySQLdb.connect(SQL_HOST, SQL_USER, SQL_PASS, SQL_DB)
		cursor = sql.cursor()
		cursor.execute('''SELECT * FROM players 
			WHERE nick = %s
			AND channel = %s''',
			(player['nick'], player['channel'],))
		row = cursor.fetchone()	

		if row:
			cursor.execute('''UPDATE players SET
				nick = %s, level = %s, login = %s, 
				last_spoken = %s, next_level = %s, 
				progress = %s
				WHERE nick = %s
				AND channel = %s''', (
					player['nick'],
					player['level'],
					player['login'],
					player['last_spoken'],
					player['next_level'],
					player['progress'], 
					player['nick'],
					player['channel'],
				)
			)
			sql.commit()
			sql.close()
			return

		cursor.execute('''INSERT INTO players 
			(nick, channel, level, login, last_spoken, next_level, progress)
			VALUES
			(%s, %s, %s, %s, %s, %s, %s)''', (
				player['nick'],
				player['channel'],
				player['level'],
				player['login'],
				player['last_spoken'],
				player['next_level'],
				player['progress'],)
		)
		sql.commit()
		sql.close()

	except Exception, e:
		# I am not sure what to do here yet, I don't want
		# the bot to dump someone to level one if the DB
		# is down...
		err('idler - db_set error: %s' % str(e))
		raise

	return


def deferred_message(channel, msg):
	''' add a message to the queue to send
	when the bot gets around to it.

	'''
	global MESSAGES
	if not channel in MESSAGES:
		MESSAGES[channel] = []

	MESSAGES[channel].append(msg)

def leaderboard(channel, top=5):
	''' return a leaderboard '''
	global IDLERS

	idlers = []
	for nick in IDLERS[channel]:
		idlers.append([
			IDLERS[channel][nick]['level'],
			nick,
		])
	idlers.sort(reverse=True)

	leaders = ["Top Idlers in %s:" % channel]
	if len(leaders) > top:
		leaders = idlers[:top]

	for l, n in leaders:
		leaders.append("%s (level %s)" % (n, l))

	return '\n'.join(leaders)

def updatePlayer(nick, channel, spoken=None):
	''' update a player, can be called periodically
	or it can be called when a user speaks to reset their
	last_spoken

	sets MESSAGES dict with anything it wants sent to the
	channel whenever (level notifications, etc).  Will return
	a message directly if it should be emitted directly (login
	notices).

	'''
	global IDLERS, TIMER, SCALER

	now = time.time()
	if not channel in IDLERS:
		IDLERS[channel] = {}

	if not nick in IDLERS[channel]:
		player = db_get(nick, channel)

		IDLERS[channel][nick] = {
			'nick': nick,
			'channel': channel,
			'level': player['level'],
			'login': now,
			'last_spoken': now,
			'next_level': player['next_level'],
			'progress': player['progress'],
		}
		db_set(IDLERS[channel][nick]) # wtf.

		classy = core.brain.getfor(nick, 'IDLER_CLASS')
		if not classy:
			return 'Logged in %s (level %i).' % (
				nick, IDLERS[channel][nick]['level'])
		
		return 'Logged in %s, the level %i %s.' % (
			nick,
			IDLERS[channel][nick]['level'],
			classy)

	player = IDLERS[channel][nick]
	player['progress'] += now - player['last_spoken']
	
	if spoken:
		player['last_spoken'] = now

	if player['progress'] < player['next_level']:
		IDLERS[channel][nick] = player
		db_set(player)
		return

	while player['progress'] >= player['next_level']:
		# person has levelled up
		player['level'] += 1
		player['next_level'] = TIMER * \
			(player['level'] ** SCALER)
		player['progress'] = player['progress'] - \
			player['next_level']

	IDLERS[channel][nick] = player
	db_set(player)

	classy = core.brain.getfor(nick, 'IDLER_CLASS')
	if not classy:
		deferred_message(channel, '%s has reached level %i!' % (
			nick, player['level']
		))
		return

	deferred_message(channel, '%s, the %s has reached level %i!' % (
		nick, classy, player['level']
	))
	return

#
# event callbacks
#
def periodic(self):
	global ACTIVE_CHANNELS, MESSAGES
	for channel in ACTIVE_CHANNELS:
		if not channel[1:] in self.chatters:
			# first call this can sometimes race
			# joining, so ignore.
			continue

		if channel in MESSAGES:
			for msg in MESSAGES[channel]:
				self.msg(channel, msg)

			MESSAGES[channel] = []

		for nick in self.chatters[channel[1:]]:
			self.msg(channel, updatePlayer(nick, channel))

def privmsg(self, user, channel, msg):
	global ACTIVE_CHANNELS
	nick = user.split('!', 1)[0]
	dest = nick
	if channel != self.nickname:
		msg = self._forMe(msg)
		if not msg:
			if channel not in ACTIVE_CHANNELS:
				return

			self.msg(channel, updatePlayer(nick, channel, True))
			return

		dest = channel

		matches = re.search(r'^\s*idlers', msg, re.I)
		if matches:
			if channel not in ACTIVE_CHANNELS:
				return
		
			self.msg(dest, updatePlayer(nick, channel, True))
			self.msg(dest, leaders(), only=True)

def userJoined(self, nick, channel):
	# JOIN counts as speaking.
	global ACTIVE_CHANNELS
	if channel not in ACTIVE_CHANNELS:
		return

	self.msg(channel, updatePlayer(nick, channel, True))

def userKicked(self, nick, channel, kicker, message):
	global ACTIVE_CHANNELS, IDLERS
	if channel not in ACTIVE_CHANNELS:
		return

	updatePlayer(nick, channel, True)
	try:
		IDLERS[channel][nick].pop()
	except KeyError:
		err('idler - KeyError on remove %s from %s ' % (
			nick, channel))

def userLeft(self, nick, channel):
	# PART counts as speaking.
	global ACTIVE_CHANNELS, IDLERS
	if channel not in ACTIVE_CHANNELS:
		return

	updatePlayer(nick, channel, True)
	try:
		IDLERS[channel][nick].pop()
	except KeyError:
		err('idler - KeyError on remove %s from %s ' % (
			nick, channel))

def userQuit(self, nick, message):
	global ACTIVE_CHANNELS, IDLERS
	for channel in IDLERS:
		if not nick in IDLERS[channel]:
			continue

		updatePlayer(nick, channel, True)
		try:
			IDLERS[channel][nick].pop()
		except KeyError:
			err('idler - KeyError on remove %s from %s ' % (
				nick, channel))

def userRenamed(self, oldname, newname):
	global ACTIVE_CHANNELS, IDLERS
	for channel in IDLERS:
		if not oldname in IDLERS[channel]:
			continue

		try:
			IDLERS[channel][newname] = \
				IDLERS[channel][oldname].pop()
			updatePlayer(newname, channel)
		except KeyError:
			err('idler - KeyError on renaming %s to %s in %s ' % (
				oldname, newname, channel))

def whoisReply(self, nick, info):
	''' When the bot joins a channel it does a 
	NAMES then a WHOIS on each name, so use this
	to trigger the login bits as we now know that
	self.chatters is populated.

	'''
	for channel in ACTIVE_CHANNELS:
		if channel[1:] not in self.chatters:
			# this should not happen, except maybe
			# for a join/part race or something.
			# worst case periodic() will get it...
			continue

		for nick in self.chatters[channel[1:]]:
			updatePlayer(nick, channel)

core.register_module(__name__)
