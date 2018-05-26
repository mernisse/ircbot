""" botlogger.py - (c) 2009-2018 Matthew J. Ernisse <matt@going-flying.com>
Provide a generic log interface for the robot wrapped around logging.

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
import logging
import logging.handlers

logger = None


def debug(s):
	""" Convenience function for logger.debug() """
	global logger
	logger.debug(s)


def err(s):
	""" Convenience function for logger.error() """
	global logger
	logger.error(s)


def logException(e):
	""" Convenience function for logger.error() with exc_info=e"""
	global logger
	logger.error("Exception: ", exc_info=e)


def log(s):
	""" Convenience function for logger.info() """
	global logger
	logger.info(s)


def setDebug(debug):
	""" Set the loglevel to either Info or Debug """
	global logger
	if debug:
		logger.setLevel(logging.DEBUG)
	else:
		logger.setLevel(logging.INFO)


logger = logging.getLogger("ircbot")
logger.setLevel(logging.DEBUG)

consoleHandler = logging.StreamHandler()
consoleHandler.setLevel(logging.DEBUG)
consoleFormatter = logging.Formatter(
	"%(asctime)s: %(message)s",
	datefmt="%b %d %H:%M:%S"
)
consoleHandler.setFormatter(consoleFormatter)

syslogHandler = logging.handlers.SysLogHandler("/dev/log")
syslogHandler.setLevel(logging.INFO)
syslogFormatter = logging.Formatter(
	"%(asctime)s ircbot: %(message)s",
	datefmt="%b %d %H:%M:%S"
)
syslogHandler.setFormatter(syslogFormatter)

logger.addHandler(consoleHandler)
logger.addHandler(syslogHandler)
logger.info("Logging initalized...")
