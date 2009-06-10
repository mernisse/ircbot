#!/usr/bin/python -tt
"""polls.py - (c) 2009 Matthew John Ernisse <mernisse@ub3rgeek.net>

Provide support for user defined polls administered by the robot.
Polls have a single question and multiple answers.  A user may answer
once.  Polls may have an end date, by default it is one month.

"""
import config
import core
import cPickle
import datetime
import os
import re
import sys

from botlogger import *

ACTIVE = []
NOTIFIES = {}
STORAGE = os.path.dirname(sys.argv[0]) + '/polls'
TRIGGER = datetime.datetime.now() - datetime.timedelta(days=1)

class Poll(object):
	owner = None
	question = ''
	answers = []
	answered = {}
	end_date = datetime.datetime.now() + \
		datetime.timedelta(days=30)

	def __init__(self, **kw):

		if not kw:
			return

		for k, v in kw.iteritems():
			try:
				getattr(self, k)
				setattr(self, k, v)
			except:
				pass

		self.save()

	def __str__(self):
		return re.sub(r'\s+', '-', self.question.lower())

	def __len__(self):
		return len(answered)

	def addanswer(self, answer):
		self.answers.append(answer)
		self.save()

	def vote(self, nick, answer):
		if answer > len(answers) - 1:
			return 'Invalid answer specified'

		answered[nick] = answer
		self.save()

		return 'Vote for %s registered' % answers[answer]

	def results(self):
		result = 'Current Results (End Date %s)\n' % self.end_date
		for a in answers:
			result += '%s - %i votes\n' % (
				a,
				len([x for x in answered.values() if x == a])
			)

		return result

	def options(self):
		result = 'Question: %s\n' % self.question
		for i, a in enumerate(self.answers):
			result += '%i) %s\n' % (i, a)

		return result

	def save(self):
		fname = '%s/%s.pkl' % (STORAGE, str(self))
		cPickle.dump(self, file(fname, 'w'), 2)

# helper functions
def show(nick):
	global ACTIVE

	result = ''

	for i, poll in enumerate(ACTIVE):
		if nick in poll.answered.keys():
			continue

		result += '--- Poll %i ---\n' % i
		result += poll.options()

	if not result:
		return 'No polls found.'

	result += 'send \'poll vote poll# answer#\' to vote'

	return result

def create(nick, args):
	global ACTIVE

	poll = Poll(owner = nick, question = args)

	ACTIVE.append(poll)
	id = len(ACTIVE)

	return 'Poll created.  Use \'poll addanswer %i answer\' to add answers' % id

def addanswer(nick, args):
	global ACTIVE

	id = int(args.split()[0])
	answer = " ".join(args.split()[1:])

	if not answer:
		return 'Invalid syntax'

	if id > len(ACTIVE) - 1:
		return 'Invalid Poll ID %i' % id

	poll = ACTIVE[id]
	poll.addanswer(answer)

	return 'Answer %s added to poll id %i' % (answer, id)

def vote(nick, args):
	global ACTIVE

	id = int(args.split()[0])
	answer = int(args.split()[1])

	if not answer:
		return 'Invalid syntax'

	if id > len(ACTIVE) - 1:
		return 'Invalid Poll ID %i' % id

	poll = ACTIVE[id]

	if nick in poll.answered.keys():
		return 'You have already voted in this poll.'

	poll.vote(nick, answer)
	return 'Your vote has been registered.'

def delete(nick, args):
	pass

def load():
	global ACTIVE, STORAGE

	for fname in os.listdir(STORAGE):
		if not re.match(r'.*\.pkl$', fname):
			continue

		poll = cPickle.load(file('%s/%s' % (STORAGE, fname)))
		if datetime.datetime.now() > poll.end_date:
			continue

		ACTIVE.append(poll)

def save():
	global ACTIVE

	for poll in ACTIVE:
		poll.save()
	
def notify(nick):
	global ACTIVE, NOTIFIES

	if nick in NOTIFIES and NOTIFIES[nick] > TRIGGER:
		return

	polls = [x for x in ACTIVE if nick not in x.answered.keys()]
	mypolls = [x for x in ACTIVE if x.owner == nick]
	NOTIFIES[nick] = datetime.datetime.now()

	if len(polls) == 0 and len(mypolls) == 0:
		return ''

	result = 'You have %i polls unanswered' % len(polls)

	if len(mypolls) > 0:
		result += ' and you have %i polls pending.' % len(mypolls)

	result += ' Send \'poll show\' to view.'
	return result

# Event handlers
def userJoined(self, user, channel):
	nick = user.split('!', 1)[0]
	notice = notify(nick)

	if notice:
		self.msg(nick, notice)

def privmsg(self, user, channel, msg):
	nick = user.split('!', 1)[0]

	if not nick:
		return

	notice = notify(nick)
	command = ''
	args = ''

	if notice:
		self.msg(nick, notice)

	if channel != self.nickname:
		msg = self._forMe(msg)
		if not msg:
			return

	matches = re.search(r'^\s*(poll)\s*(\w+)', msg, re.I)

	if not matches:
		return

	command = matches.group(2)
	args = re.sub(r'^\s*poll\s*\w+\s+', '', msg, re.I)

	if command == 'show':
		msg = show(nick)
		for m in msg.split('\n'):
			self.msg(nick, m)

		return

	elif command == 'create':
		self.msg(nick, create(nick, args))
		return

	elif command == 'vote':
		self.msg(nick, vote(nick, args))
		return

	elif command == 'results':
		try:
			poll = ACTIVE[int(args)]
		except:
			self.msg(nick, 'Cannot fetch poll id %s' % args)
			return

		if nick not in config.owners and \
			not nick == poll.owner and \
			nick not in poll.answered.keys():
			self.msg(nick, 'You are not allowed to view this yet')
			return
	
		msg = poll.results()
		for m in msg.split('\n'):
			self.msg(nick, m)

	elif command == 'addanswer':
		msg = addanswer(nick, args)
		self.msg(nick, msg)
		return

	elif command == 'delete':
		pass

	else:
		self.msg(nick, 'Invalid command %s.' % command)

core.MODULES.append(__name__)
load()
log('%s loaded with %i polls active' % (__name__, len(ACTIVE)))
