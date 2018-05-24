""" nethack.py (c) 2009, 2013 - 2018 Matthew J. Ernisse <matt@going-flying.com>

Module for the IRC robot that implements similar function to the Nethack
witty sayings.

Requires pom.py (ported from OpenBSD's pom.c) for Phase of Moon detection.

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
from os import stat
from pom import pom
from random import randint
import re
from stat import ST_MTIME
from time import time

from botlogger import debug, err, log, logException

NH_FIRED = {}
FORTUNES = []
FORTUNES_TSTAMP = 0


def load_fortunes():
	global FORTUNES, FORTUNES_TSTAMP

	#
	# only reload fortunes if the file has changed since we loaded it.
	#
	tstamp = stat("nethack.nki")[ST_MTIME]
	if tstamp < FORTUNES_TSTAMP:
		return True

	try:
		new_fortunes = []
		with open("nethack.nki") as fd:
			for line in fd:
				line = re.sub("#.*", "", line.strip())
				if not line:
					continue
				new_fortunes.append(line)

		FORTUNES = new_fortunes
		FORTUNES_TSTAMP = tstamp
	except Exception as e:
		logException(e)
		return None

	return True


def privmsg(self, user, channel, msg):
	msg = self._forMe(msg)
	if not msg:
		return False

	dst = user.split('!', 1)[0]
	if channel != self.nickname:
		dst = channel

	curPom = pom()
	if curPom < config.getInt("pom_high") and curPom > config.getInt("pom_low"):
		return False

	# The "Phase of the moon" is 99% - 100% or 0% - 1%;
	# let's play ball.
	global NH_FIRED
	if dst not in NH_FIRED.keys():
		NH_FIRED[dst] = 0

	if NH_FIRED[dst] > (time() - config.getInt("backoff")):
		# We fired recently (within the last 2h), so
		# please donut annoy the channel.
		return

	if not load_fortunes():
		self.msg(dst, "The filesystem error hits! Your nethack.nki turns to dust!--More--")
		NH_FIRED[dst] = time()

	if len(FORTUNES) > 0:
		NH_FIRED[dst] = time()
		self.msg(dst, FORTUNES[randint(0, len(FORTUNES) - 1)])


#
# preload fortunes.
#
if load_fortunes():
	log('nethack: %i fortunes loaded' % (len(FORTUNES)))

config = core.config.getChildren("nethack")
core.register_module(__name__)
