"""testmod.py - (c) 2009 Matthew John Ernisse <mernisse@ub3rgeek.net>

Provide a demo for the plugin functionality.

"""
import core
from botlogger import *

core.MODULES.append(__name__)

def action(self, user, channel, msg):
	err('TESTMODULE: GOT ACTION %s' % msg)

