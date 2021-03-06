""" hateball.py (c) 2013 - 2018 Matthew J. Ernisse <matt@going-flying.com>

Module for irc bot that implements a magic hate ball-esque reply of last
resort for directed speech to the bot.  This should be listed *last* in
the "modules" section of config.json as it prevents any further callbacks
in the list from running.

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
import random
import re
import json

from botlogger import debug, err, log, logException

FATES = ''


def privmsg(self, user, channel, msg):
	""" If anything makes it to this callback in the form of
	<nick>: <ANYTHING> then reply with a random line of text from
	fates.json.  No further callbacks will be processed after this.
	"""
	global FATES

	msg = self._forMe(msg)
	if not msg:
		return

	speaker = user.split('!', 1)[0]
	dst = channel

	if not FATES:
		return

	hatred = FATES[random.randint(0, len(FATES) - 1)]
	self.msg(dst, "{}: {}".format(speaker, hatred), only=True)


#
# Load fates at import
#
try:
	with open(os.path.join(core.dataDir, 'fates.json')) as fd:
		for line in fd:
			FATES = FATES + line.strip()

		FATES = json.loads(FATES)
		log("hateball loaded {} fates".format(len(FATES)))

except Exception as e:
	logException(e)

core.register_module(__name__)
