#!/usr/bin/python -tt
''' idler.py (c) 2013 Matthew J Ernisse <mernisse@ub3rgeek.net>

Implement an idle tracker - this is NOT IdleRPG like in that it
does not ''penalize users'' for talking, it just keeps track of
idle time.

TODO:
	- Maybe add combat?  Would need to figure out a scaling
	attack power system or something.

'''

import core
import time
import private
import random
import re
import MySQLdb

from botlogger import *

ACTIVE_CHANNELS = ['#adultflirt'] # list of channels to care about.
AP_SCALE = 25 # level * AP_SCALE = max attackpower
IDLERS = {}   # players
MESSAGES = {} # waiting messages
SCALER = 1.4  # exponent to scale the next level by
TIMER = 14400 # base timer for each level

SQL_HOST = private.IDLERS_SQL_HOST
SQL_USER = private.IDLERS_SQL_USER
SQL_PASS = private.IDLERS_SQL_PASS
SQL_DB = private.IDLERS_SQL_DB

def battle(channel, force=None):
	''' execute a battle '''
	global AP_SCALE, IDLERS, MESSAGES

	if not force:
		if random.randint(0,100) < 97:
			return

	possible_nicks = IDLERS[channel].keys()
	attacker = possible_nicks[random.randint(0, len(possible_nicks) - 1)]

	for x in range(0, 10):
		victim = \
			possible_nicks[random.randint(0, len(possible_nicks) - 1)]

		if attacker != victim:
			break

	else:
		return

	a_max = int(IDLERS[channel][attacker]['level']) * AP_SCALE
	v_max = int(IDLERS[channel][victim]['level']) * AP_SCALE

	a_roll = random.randint(0, a_max)
	v_roll = random.randint(0, v_max)

	log('%s (%i/%i) attacked %s (%i/%i)' % (
		attacker, a_roll, a_max, victim, v_roll, v_max
	))

	msg = "%s (%i/%i) came upon %s (%i/%i) and attacked them!" % (
		attacker, a_roll, a_max, victim, v_roll, v_max
	)

	if a_roll == 0:
		# Critical Miss!
		msg += "Unfortunatly %s tripped and fell."
		msg += " This calamity cost them 30%% of their slack!"
		deferred_message(channel, msg % (attacker))

		progress = IDLERS[channel][attacker]['progress']
		IDLERS[channel][attacker]['progress'] = progress * 0.70
		db_set(IDLERS[channel][attacker])
		return

	if a_roll == a_max:
		# Critical Hit!
		msg += " %s becomes imbued with the power of their God!"
		msg += " This blessing grants them 20%% slack!"
		deferred_message(channel, msg % (attacker))

		progress = IDLERS[channel][attacker]['progress']
		IDLERS[channel][attacker]['progress'] = progress * 1.20
		db_set(IDLERS[channel][attacker])
		return
		
	if a_roll <= v_roll:
		if victim.lower() == 'lee':
			msg += " %s dodges behind a pack of dogs!"
		elif victim.lower() == 't':
			msg += " %s defends themself lazily!"
		else:
			msg += " %s defended themself valiantly!"

		deferred_message(channel, msg % (victim))
		return

	if a_roll >= v_roll:
		msg += " %s is victorious and is rewarded with 10%% more slack!"
		deferred_message(channel, msg % (attacker))

		progress = IDLERS[channel][attacker]['progress']
		IDLERS[channel][attacker]['progress'] = progress * 1.10
		db_set(IDLERS[channel][attacker])
		return
	
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
		now = time.time()
		player = {
			'nick': nick,
			'channel': channel,
			'level': 1,
			'checked': now,
			'next_level': TIMER,
			'progress': 0.0,
			'last_spoken': now,
		}
		return player

	# id | nick | channel | level | login | checked | next_level | 
	# progress | last_spoken
	player = {}
	player['level'] = int(row[3])
	player['checked'] = float(row[5])
	player['next_level'] = int(row[6])
	player['progress'] = float(row[7])
	player['last_spoken'] = float(row[8])

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
				checked = %s, next_level = %s, 
				progress = %s, last_spoken = %s
				WHERE nick = %s
				AND channel = %s''', (
					player['nick'],
					player['level'],
					player['login'],
					player['checked'],
					player['next_level'],
					player['progress'], 
					player['last_spoken'], 
					player['nick'],
					player['channel'],
				)
			)
			sql.commit()
			sql.close()
			return

		cursor.execute('''INSERT INTO players 
			(nick, channel, level, login, checked, next_level, progress, last_spoken)
			VALUES
			(%s, %s, %s, %s, %s, %s, %s, %s)''', (
				player['nick'],
				player['channel'],
				player['level'],
				player['login'],
				player['checked'],
				player['next_level'],
				player['progress'],
				player['last_spoken'],)
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

def event(channel):
	''' Have a calamity or blessing happen to a player. '''
	global IDLERS

	if random.randint(0, 1000) < 994:
		return

	blessings = [
		'%s spent the year dead for tax reasons!',
		'%s drank a Pan Galactic Gargle Blaster.',
		'%s was picked up by the wake of the passing Heart of Gold.',
	]

	calamities = [
		'%s was turned into a pot of petunias.',
		'%s was waylayed by a rogue telephone cleaner.',
		'%s has been insulted by Wowbagger the Infinitely Prolonged.',
	]

	possible_nicks = IDLERS[channel].keys()
	victim = possible_nicks[random.randint(0, len(possible_nicks) - 1)]

	# 70/30% chance of a blessing vs calamity
	if random.randint(0, 100) <= 70:
		msg = blessings[random.randint(0, len(blessings) - 1)]
		msg += "  This blessing has granted them 20%% slack!"
		slack = 1.2
	else:
		msg = calamities[random.randint(0, len(calamities) - 1)]
		msg += "  This terrible calamity has cost them 20%% slack!"
		slack = 0.8

	deferred_message(channel, msg % (victim))
	progress = IDLERS[channel][victim]['progress']
	IDLERS[channel][victim]['progress'] = progress * slack
	db_set(IDLERS[channel][victim])
	return
	
def leaderboard(channel, top=5):
	''' return a leaderboard '''
	global IDLERS

	idlers = []
	for nick in IDLERS[channel]:
		classy = core.brain.getfor(nick, 'IDLER_CLASS')
		pretty_name = nick
		if classy:
			pretty_name = '%s the %s' % (
				nick, classy)
			
		idlers.append([
			IDLERS[channel][nick]['level'],
			nick,
		])

	idlers.sort(reverse=True)

	leaders = ["Top Idlers in %s:" % channel]
	if len(leaders) > top:
		leaders = idlers[:top]

	for l, n in idlers:
		leaders.append("%s (level %s)" % (n, l))

	return '\n'.join(leaders)

def updatePlayer(nick, channel, spoken=None):
	''' update a player, can be called periodically
	or it can be called when a user speaks to reset their
	checked

	sets MESSAGES dict with anything it wants sent to the
	channel whenever (level notifications, etc).  Will return
	a message directly if it should be emitted directly (login
	notices).

	'''
	global IDLERS, TIMER, SCALER
	if nick == core.nickname:
		# no fair letting the bot play
		return

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
			'checked': now,
			'next_level': player['next_level'],
			'progress': player['progress'],
			'last_spoken': player['last_spoken'],
		}
		db_set(IDLERS[channel][nick])

	player = IDLERS[channel][nick]
	player['progress'] += now - player['checked']
	player['checked'] = now

	if spoken:
		# most IRC clients don't think of you as 'IDLE'
		# until 5 minutes of no activity has passed.
		if now - player['last_spoken'] >= 300:
			player['progress'] -= 300

		player['last_spoken'] = now

	levelled = False
	if player['progress'] >= player['next_level']:
		# person has levelled up
		player['level'] += 1
		player['progress'] -= player['next_level']
		player['next_level'] = int(TIMER * \
			(player['level'] ** SCALER))
		levelled = True


	IDLERS[channel][nick] = player
	db_set(player)

	if not levelled:
		return

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
		if channel not in self.chatters:
			# first call this can sometimes race
			# joining, so ignore.
			continue

		# Ready?  FIGHT!
		battle(channel)
		event(channel)

		if channel in MESSAGES:
			for msg in MESSAGES[channel]:
				self.msg(channel, msg)

			MESSAGES[channel] = []

		for nick in self.chatters[channel]['users']:
			updatePlayer(nick, channel)

def privmsg(self, user, channel, msg):
	global ACTIVE_CHANNELS
	nick = user.split('!', 1)[0]
	dest = nick
	if channel != self.nickname:
		if channel in ACTIVE_CHANNELS:
			updatePlayer(nick, channel, True)

		msg = self._forMe(msg)
		if not msg:
			return

		dest = channel

	#
	# public commands
	#
	matches = re.search(r'^\s*idlers', msg, re.I)
	if matches:
		self.msg(dest, leaderboard(channel), only=True)

	#
	# priv. commands
	#
	if nick not in self.owners:
		return

	matches = re.search(r'^\s*playerdump', msg, re.I)
	if matches:
		self.msg(nick, 'Players:\n%s' % str(IDLERS), only=True)

	matches = re.search(r'^\s*playerbattle\s+(#[a-z0-9_]+)\s*', msg, re.I)
	if matches:
		c = matches.group(1)
		if not c in ACTIVE_CHANNELS:
			self.msg(nick, '%s is an invalid channel name.' % (c),
				only=True)

		battle(c, True)
		self.msg(nick, 'A wild idler appears in %s!' % c, only=True)

	matches = re.search(r'^\s*idlesave', msg, re.I)
	if matches:
		for chan in ACTIVE_CHANNELS:
			self.msg(nick, 'saving users for %s' % chan)
			
			for player in IDLERS[chan]:
				self.msg(nick, player)
				updatePlayer(player, chan)
		
		raise core.StopCallBacks

def userJoined(self, nick, channel):
	global ACTIVE_CHANNELS
	if channel not in ACTIVE_CHANNELS:
		return

	updatePlayer(nick, channel, True)

def userKicked(self, nick, channel, kicker, message):
	global ACTIVE_CHANNELS, IDLERS
	if channel not in ACTIVE_CHANNELS:
		return

	updatePlayer(nick, channel, True)
	try:
		IDLERS[channel].pop(nick)
	except KeyError:
		err('idler - KeyError on remove %s from %s ' % (
			nick, channel))

def userLeft(self, nick, channel):
	global ACTIVE_CHANNELS, IDLERS
	if channel not in ACTIVE_CHANNELS:
		return

	updatePlayer(nick, channel, True)
	try:
		IDLERS[channel].pop(nick)
	except KeyError:
		err('idler - KeyError on remove %s from %s ' % (
			nick, channel))

def userQuit(self, nick, message):
	global ACTIVE_CHANNELS, IDLERS
	for channel in IDLERS:
		if nick not in IDLERS[channel]:
			continue

		updatePlayer(nick, channel, True)
		try:
			IDLERS[channel].pop(nick)
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
				IDLERS[channel].pop(oldname)
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
	global ACTIVE_CHANNELS
	for channel in ACTIVE_CHANNELS:
		if channel not in self.chatters:
			# this should not happen, except maybe
			# for a join/part race or something.
			# worst case periodic() will get it...
			continue

		for nick in self.chatters[channel]['users']:
			updatePlayer(nick, channel)

core.register_module(__name__)