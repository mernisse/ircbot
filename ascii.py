""" ascii.py (c) 2013 - 2018 Matthew J. Ernisse <matt@going-flying.com>
All Rights Reserved.

ASCII Art bot actions.

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
import os
import re

from botlogger import logException


def privmsg(self, user, channel, msg):
	""" Listen for <nick>: ascii <word> and emit the contents of
	<botdir>/ascii/<word>.txt back to the channel from whence the
	message came.
	"""
	dst = user.split('!', 1)[0]
	if channel != self.nickname:
		msg = self._forMe(msg)
		if not msg:
			return None

		dst = channel

	matches = re.search(r'^ascii\s+([a-z0-9_.-]+)\s*$', msg, re.IGNORECASE)
	if not matches:
		return

	what = matches.group(1).lower()

	if what == 'list':
		try:
			available = []
			files = os.listdir('ascii/')
			for f in files:
				if not f.endswith('.txt'):
					continue
				fn, ext = os.path.splitext(os.path.basename(f))
				available.append(fn)

		except Exception as e:
			logException(e)
			self.msg(dst, "It's a secret.")

		self.msg(dst, ' '.join(available), only=True)

	art = ascii(what)
	if not art:
		raise core.StopCallBacks

	if type(art) == str:
		self.msg(dst, art)
		raise core.StopCallBacks

	for line in art:
		if line == '\n':
			line = ' '
		self.msg(dst, line)

	raise core.StopCallBacks


def ascii(what):
	""" Given <word> that was parsed out of the message in privmsg()
	read the file from disk and return the contents as a list..
	"""
	# The utterance regex above only matches these characters, but
	# we'll double-check, Just In Case.
	if not re.search(r'^[a-z0-9_.-]+$', what):
		return "Nope, not gonna do it."

	try:
		fd = open("ascii/%s.txt" % (what))
	except:
		return "I do not know of what you speak."

	art = fd.readlines()
	fd.close()
	return art


core.register_module(__name__)
