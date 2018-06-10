""" crier.py - (c) 2018 Matthew J. Ernisse <matt@going-flying.com>

Say certain things when various commands are given.

This splits words spoken in a channel either to the bot (nick: things)
or prefixed with a ! (!things and more things) and traverses a section
of the config.json tree rooted at "crier".  This lets complex responses
happen.

For example:

"crier": {
	"dance": {
		"for": {
			"me": {
				"response": "no."
			},
			"us": {
				"response": "sigh."
			}
		}
	},
	"faq": {
		"response": [
			"This is a FAQ",
			"There are questions",
			"There are answers."
		]
	}
}

The above would cause "dance for me" to be responded to with "no." but
"dance for us" to be responded to with "sigh.".  Note traversal stops at
the first node with a "response" key in it.

Presently that means one could not have "dance for me please" do anything
different from "dance for me".


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
from botlogger import debug, err, log, logException

COMMANDS = {}


def privmsg(self, user, channel, msg):
	if channel == self.nickname:
		return

	strippedMsg = self._forMe(msg)
	if not strippedMsg and not msg.startswith("!"):
		return

	if strippedMsg:
		msg = strippedMsg

	words = msg.split()
	if words[0].startswith("!"):
		words[0] = words[0][1:]

	commandBranch = COMMANDS
	for word in words:
		if word not in commandBranch.keys():
			return

		commandBranch = commandBranch[word]
		if "response" in commandBranch.keys():
			if type(commandBranch["response"]) == str:
				commandBranch["response"] = [commandBranch["response"]]

			for line in commandBranch["response"]:
				self.msg(channel, line)


COMMANDS = core.config.getChildren("crier").config
core.MODULES.append(__name__)
