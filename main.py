#!/usr/bin/env python3
''' main.py (c) 2013 - 2018 Matthew Ernisse <matt@going-flying.com>
All Rights Reserved

This is the main module of the IRC robot.  I envision him as Marvin, The
Paranoid Android.

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
import bot
import sys

from botlogger import *
from twisted.internet import reactor
from twisted.internet.ssl import ClientContextFactory


if __name__ == '__main__':
	hostname = core.config.getStr("host")
	portnum = core.config.getInt("port")

	if core.config.getBool("ssl"):
		log('Connecting to {}:{} with SSL'.format(hostname, portnum))
		reactor.connectSSL(hostname, portnum,
			bot.BotFactory(core.config), ClientContextFactory())
	else:
		log('Connecting to {}:{}'.format(hostname, portnum))
		reactor.connectTCP(hostname, portnum, bot.BotFactory(core.config))

	reactor.run()
