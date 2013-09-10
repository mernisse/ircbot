#!/usr/bin/python -tt
''' core.py - (c) 2009, 2013 Matthew John Ernisse <mernisse@ub3rgeek.net>
provide core functions for the bot

The MODULES list holds all the names for the plugins registered to the
bot.  Each plugin should import core and call core.register_module(__name__)
to ensure it is present in this list.  Failure to do so will cause the
callbacks to never get processed.

This could be useful if you want to extend parts of the bot but not register
callbacks.

'''
import pickle
import re
from botlogger import *

MODULES = []

class Brain(dict):
	''' Implement a simple persistant key, value storage object.  This 
	saves state by overloading __setitem__ and __delitem__ to pickle the
	object to disk and __init__ to load the object from disk.

	The file to pickle to/from is stored as the fn attribute.

	'''
	fn = 'mybrain.pkl'

	def __init__(self, **kwargs):
		''' create a new Brain.  If a mapping is specified with the
		constructor then it OVERWRITES any existing saved state.

		'''
		self._load()
		super(Brain, self).__init__(**kwargs)

	def _load(self):
		''' Load the object from disk '''
		if not os.path.exists(self.fn):
			return

		fd = open(self.fn, 'r')

		selfie = pickle.load(fd)
		fd.close()

		for k,v in selfie.iteritems():
			log('loaded %i items for %s' % (len(v), k))
			super(Brain, self).__setitem__(k, v)

	def _save(self):
		''' Save the object to disk '''

		fd = open(self.fn, 'wb')
		pickle.dump(self, fd)
		fd.close()

		log('wrote brain to disk')

	def __delitem__(self, k):
		''' B.__delitem__(k) <==> del B[k] '''
		super(Brain, self).__delitem__(k)

		self._save()

	def __setitem__(self, k, v):
		''' B.__setitem__(k, v) <==> B[k] = v '''
		super(Brain, self).__setitem__(k, v)

		self._save()

	def getfor(self, who, k, default=None):
		''' B.getfor(w,k[,d]) -> B[w][k] if k in w and w in B else d.'''
		try:
			return self[who][k]
		except KeyError:
			return default

class StopCallBacks(Exception):
	''' Exception to stop processing callbacks '''
	pass

def privmsg(self, user, channel, msg):
		''' Bot control actions, both public and private. '''
		nick = user.split('!', 1)[0]
		dest = nick

		if channel != self.nickname:
			message = self._forMe(msg)
			if not message:
				return

			dest = channel

		#
		# public bot responses
		#
		matches = re.search(r'^\s*help', msg, re.I)
		if matches:
			self.msg(dest,
				'Visit http://mernisse.github.io/ircbot',
				only=True)

		#
		# bot control actions are only honored from owners and are
		# returned via PRIVMSG back to the owner (not the channel, if
		# originally uttered in public.
		#
		if not nick in self.owners:
			return

		matches = re.search(r'^\s*reload\s+([a-z0-9_]+)\s*$', msg)
		if matches:
			module = matches.group(1)
			if module not in sys.modules:
				self.msg(nick,
					'Module %s is not loaded.' % module,
					only=True)

			log('Reloading module %s at request of %s' % (
				module,
				nick
			))

			# I am told twisted's rebuild is better than the
			# built in reload().
			rebuild(sys.modules[module])
			self.msg(nick,
				'Module %s reloaded.' % module, only=True)

		matches = re.search(r'^\s*join\s+(#[a-z0-9_]+)\s*$', msg)
		if matches:
			channel = matches.group(1)
			if channel in self.chatters:
				self.msg(nick,
					'Already in %s' % channel, only=True)

			self.join(channel)
			self.msg(nick,
				'Joined %s' % channel, only=True)

		matches = re.search(r'^\s*leave\s+(#[a-z0-9_]+)\s*$', msg)
		if matches:
			channel = matches.group(1)
			if channel not in self.chatters:
				self.msg(nick, 'Not in %s' % channel, only=True)

			self.leave(channel, '%s has banished me.' % nick)
			self.msg(nick, 'Left %s' % channel, only=True)

		matches = re.search(r'^\s*spy\s*$', msg)
		if matches:
			self.msg(nick, 
				'Chatters:\n%s' % str(self.chatters), only=True)

def register_module(module):
	''' Register your module with the bot so that your callbacks will
	be called when an event happens.

	'''
	global MODULES
	if module not in MODULES:
		MODULES.append(module)
		log('%s Registered.' % module)
	else:
		log('%s Reloaded.' % module)

brain = Brain()
register_module(__name__)
