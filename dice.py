''' dice.py (c) 2021 Matthew J. Ernisse <matt@going-flying.com>

Roll some dice.

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
import random
import re

from botlogger import *


def privmsg(self, user, channel, msg):
	dst = user.split('!', 1)[0]
	if channel != self.nickname:
		msg = self._forMe(msg)
		if not msg:
			return

		dst = channel

	matches = re.search(
		r'(?P<cnt>\d+)?\s*[dD](?P<sides>\d+)(\s*\+(?P<add>\d+))?',
		msg,
		re.I
	)

	if not matches:
		return

	add = matches.group('add')
	cnt = matches.group('cnt')
	sides = matches.group('sides')

	try:
		sides = int(sides)
	except Exception:
		return

	if sides > 100 or sides < 2:
		return

	if not add:
		add = 0
	else:
		add = int(add)

	if not cnt:
		cnt = 1
	else:
		cnt = int(cnt)

	result = 0
	rolls = []
	for x in range(0, cnt):
		roll = random.randint(1, sides)
		rolls.append(str(roll))
		result += roll

	result += add
	rolls = ', '.join(rolls)

	msg_add = ''
	if add > 0:
		msg_add = f' and added {add}'

	self.msg(
		dst,
		f'Rolled {cnt} D{sides} ({rolls}){msg_add}, and got {result}.',
		only=True
	)


core.register_module(__name__)
