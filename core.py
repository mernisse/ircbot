""" core.py - (c) 2009, 2013 - 2018 Matthew J. Ernisse <matt@going-flying.com>

Provide core functions for the bot

The MODULES list holds all the names for the plugins registered to the
bot.  Each plugin should import core and call core.register_module(__name__)
to ensure it is present in this list.  Failure to do so will cause the
callbacks to never get processed.

This could be useful if you want to extend parts of the bot but not register
callbacks.

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
import importlib
import json
import os
import re
import subprocess
import sys
from botlogger import debug, err, log, logException, setDebug
from twisted.python.rebuild import rebuild

__version__ = "2.0.0"
nickname = ''
MODULES = []


class Configuration(object):
	""" Parse and hold a JSON configuration while providing some convenience
	accessors.
	"""
	def __init__(self, fileName=None):
		self.config = {}
		if fileName:
			self.load(fileName)

	def _combine(self, src, tgt):
		""" Deep merge tgt into src, modifying src. """
		for k, v in tgt.items():
			if k in src.keys() and isinstance(src[k], dict):
				self._combine(src[k], v)
			else:
				src[k] = v

	def load(self, fileName):
		""" Load fileName.json and optionally fileName.private.json and
		store the parsed object as Configuration.config.
		"""
		if not os.path.exists(fileName):
			return

		log("Loading {}".format(fileName))
		with open(fileName) as fd:
			obj = json.load(fd)

		self.config = obj

		fn, ext = os.path.splitext(fileName)
		pvtFileName = "{}.private{}".format(fn, ext)
		if os.path.exists(pvtFileName):
			log("Loading {}".format(pvtFileName))
			with open(pvtFileName) as fd:
				obj = json.load(fd)

			self._combine(self.config, obj)

	def getBool(self, key):
		""" Returns key as a bool, returns None if it does not exist. """
		if key not in self.config.keys():
			return None

		return bool(self.config[key])

	def getChildren(self, key):
		""" Return a Configuration object with a view of the given subtree."""
		if key not in self.config.keys():
			raise KeyError("Requested key {} not found.".format(key))

		children = Configuration(None)
		children.config = self.config[key]
		return children

	def getInt(self, key, default=None):
		""" Returns key as an int, returns default if set if the key does
		not exist or raises a KeyError.
		"""
		if key not in self.config.keys():
			if default:
				return default

			raise KeyError("Requested key {} not found.".format(key))

		return int(self.config[key])

	def getList(self, key):
		""" Convenince function for self.config.get(key, []) """
		return self.config.get(key, [])

	def getStr(self, key):
		""" Convenince function for self.config.get(key, "") """
		return self.config.get(key, "")


class StopCallBacks(Exception):
	""" Signal to Bot() to stop processing callbacks in the stack."""
	pass


def load_modules(modules):
	""" Import the requested modules. """
	for module in modules:
		try:
			importlib.import_module(module)
		except ImportError as e:
			err("failed to import {}".format(module))
			logException(e)


def privmsg(self, user, channel, msg):
		''' Bot control actions, both public and private. '''
		global MODULES
		nick = user.split('!', 1)[0]
		dest = nick

		if channel != self.nickname:
			msg = self._forMe(msg)
			if not msg:
				return

			dest = channel

		#
		# public bot responses
		#
		matches = re.search(r'^\s*help', msg, re.I)
		if matches:
			self.msg(
				dest,
				"I'm sorry Dave, I can't help you.",
				only=True
			)

		#
		# bot control actions are only honored from owners and are
		# returned via PRIVMSG back to the owner (not the channel, if
		# originally uttered in public.
		#
		if nick not in self.owners:
			return

		matches = re.search(r'^\s*reload\s+([a-z0-9_]+)\s*$', msg)
		if matches:
			module = matches.group(1)
			if module not in sys.modules:
				self.msg(
					nick,
					"Module {} is not loaded.".format(module),
					only=True
				)

			log('Reloading module {} at request of {}'.format(
				module,
				nick
			))

			# I am told twisted's rebuild is better than the
			# built in reload().
			rebuild(sys.modules[module])
			self.msg(
				nick,
				"Module {} reloaded.".format(module),
				only=True
			)

		matches = re.search(r'^\s*debug\s*$', msg, re.I)
		if matches:
			if self.debug:
				self.debug = False
			else:
				self.debug = True

			setDebug(self.debug)
			self.msg(
				nick,
				"Debug is now {}".format(self.debug),
				only=True
			)

		matches = re.search(r'^\s*join\s+(#[a-z0-9_]+)\s*$', msg)
		if matches:
			channel = matches.group(1)
			if channel in self.chatters:
				self.msg(
					nick,
					"Already in {}".format(channel),
					only=True
				)

			self.join(channel)
			self.msg(
				nick,
				'Joined {}'.format(channel),
				only=True
			)

		matches = re.search(r'^\s*leave\s+(#[a-z0-9_]+)\s*$', msg)
		if matches:
			channel = matches.group(1)
			if channel not in self.chatters:
				self.msg(nick, 'Not in {}'.format(channel), only=True)

			self.leave(channel, '{} has banished me.'.format(nick))
			self.msg(nick, 'Left {}'.format(channel), only=True)

		matches = re.search(r'^\s*spy\s*$', msg)
		if matches:
			self.msg(
				nick,
				'Chatters:\n{}'.format(str(self.chatters)),
				only=True
			)

		matches = re.search(r'^\s*listmods\s*', msg, re.I)
		if matches:
			self.msg(
				nick,
				'Loaded Modules: {}.'.format(','.join(MODULES)),
				only=True
			)


def register_module(module):
	''' Register your module with the bot so that your callbacks will
	be called when an event happens.

	'''
	global MODULES
	if module not in MODULES:
		MODULES.append(module)
		log('{} Registered.'.format(module))
	else:
		log('{} Reloaded.'.format(module))


try:
	revision = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'])
	__version__ = "{}-{}".format(__version__, revision.strip().decode())
except:
	pass

config = Configuration("config.json")
dataDir = os.path.join(
	os.path.abspath(os.path.dirname(sys.argv[0])),
	"data"
)
print("Data dir: {}, Version: {}".format(dataDir, __version__))
register_module(__name__)
load_modules(config.getList("modules"))
