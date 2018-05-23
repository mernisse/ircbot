# coding: utf-8 
"""__init__.py - (c) 2013 - 2018 Matthew J. Ernisse <matt@going-flying.com>

Catch, log, and shorten urls.  Uses uber.hk because that is mine.

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
from botlogger import *

from . import handlers

__all__ = ["handlers"]

def privmsg(self, user, channel, msg):
	''' Module hook function for the ircbot.  Called on receipt of
	a privmsg.

	'''
	speaker = user.split('!', 1)[0]

	#
	# look for a url in the incoming text
	#
	urls = handlers.core.detect_valid_urls(msg)
	if not urls:
		return

	try:
		for url in urls:
			debug('uberurls - processing url: {}'.format(url))
			url, title = handlers.processurl(url)

			debug('uberurls - {} mentioned url: {}, title: {})'.format(
				speaker,
				url,
				title
			))
			self.msg(channel, "{} [{}]".format(url, title))

	except Exception as e:
		logException(e)

	raise core.StopCallBacks

core.register_module(__name__)
