""" autoop.py (c) 2013 - 2018 Matthew J. Ernisse <matt@going-flying.com>
All Rights Reserved.

Automatically try to +o people who join the channel with a matching usermask

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
import re
import time


def check_masks(userhost):
	for mask in core.config.getChildren("autoop").getList("masks"):
		if re.search(mask, userhost):
			return True

	return False


def whoisReply(self, nick, userinfo):
	if 'username' not in userinfo or \
		'hostname' not in userinfo:
		return

	if nick == self.nickname:
		return

	userhost = "%s@%s" % (userinfo['username'], userinfo['hostname'])

	if not check_masks(userhost):
		return

	for channel in self.chatters:
		if nick in self.chatters[channel]['users']:
			self.mode(channel, True, "o", user=nick)


core.register_module(__name__)
