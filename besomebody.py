''' besomebody.py (c) 2013 - 2018 Matthew J. Ernisse <matt@going-flying.com>

Impersonate a variety of folks.

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
'''
import core
import os
import random
import re

from botlogger import logException


def afraid():
	'''I am not the Kwisatz Haderach...'''
	litany = [
		'I must not fear.',
		'Fear is the mind-killer.',
		'Fear is the little-death that brings total obliteration.',
		'I will face my fear.',
		'I will permit it to pass over me and through me.',
		'And when it has gone past I will turn the inner eye to see its path.',
		'Where the fear has gone there will be nothing.',
		'Only I will remain.',
	]
	return '\n'.join(litany)


def bhanat():
	''' /me pours a little out for his homies who are not here. '''
	ticketnum = random.randint(10000, 999999)
	return "<postit>%s</postit>" % str(ticketnum)


def quote_from_disk(who, index=None):
	''' emit a quote from nicks/who.txt '''
	sayings = []
	try:
		with open(os.path.join(core.dataDir, "nick/{}.txt".format(who))) as fd:
			line = fd.readline()
			if line:
				sayings.append(line)

	except Exception as e:
		logException(e)
		return "I do not know of whom you speak."

	if not index:
		index = random.randint(0, len(sayings) - 1)

	return sayings[index]


def privmsg(self, user, channel, msg):
	""" Look for <nick>: be <word> and dispatch <word> to the various
	handlers.  If one of the handlers returns something then it will
	be sent back to the channel.
	"""
	dst = user.split('!', 1)[0]
	if channel != self.nickname:
		msg = self._forMe(msg)
		if not msg:
			return

		dst = channel

	matches = re.search(
		r'^be\s+([a-z0-9_.-]+)(?:\[(\d+)\])?\s*$',
		msg,
		re.I
	)

	if not matches:
		return

	who = matches.group(1).lower()

	if not re.search(r'^[a-z0-9_.-]+$', who):
		return "Nope, not gonna do it."

	if who == "bhanat":
		self.msg(dst, bhanat(), only=True)

	elif who == "afraid":
		self.msg(dst, afraid(), only=True)

	else:
		index = matches.group(2)
		self.msg(dst, quote_from_disk(who, index), only=True)


core.register_module(__name__)
