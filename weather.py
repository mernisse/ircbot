#!/usr/bin/python -tt
''' weather.py (c) 2016 Matthew J. Ernisse <matt@going-flying.com>

Emit weather information from the Yahoo API.

'''

import core
import re
import pywapi

from botlogger import *

def get_weather(location):
	''' Get weather for a location string. '''
	location = unicode(location)
	wx = pywapi.get_weather_from_weather_com(location, units='imperial')
	if "error" in wx:
		return wx["error"]

	wx = wx.get("current_conditions", None)
	if not wx:
		return "Failed to fetch weather."

	return "At %s it is %s degF (feels like %s) and %s" % (
		wx["station"],
		wx["temperature"],
		wx["feels_like"],
		wx["text"]
	)

def privmsg(self, user, channel, msg):
	dst = user.split('!', 1)[0]
	speaker = dst
	if channel != self.nickname:
		msg = self._forMe(msg)
		if not msg:
			return

		dst = channel

	matches = re.search(
		r'^weather:?\s*([0-9]{,5})\s*$',
		msg,
		re.I
	)

	if not matches:
		return

	location = matches.group(1).lower()
	if not location:
		location = core.brain.getfor(speaker, 'WXLOCATION')
		if not location:
			self.msg(dst, "I can't remember your location.")
			self.msg(dst,
				"Use ``set wxlocation zipcode'' to remind me.",
				only=True)
			return

	try:
		msg = get_weather(location)

	except Exception, e:
		log('weather() failed to fetch wx for  %s, %s' % (
			location, str(e)
		))
		self.msg(dst, "Failed to fetch the weather.", only=True)
		return

	self.msg(dst, msg, only=True)

core.register_module(__name__)
