#!/usr/bin/python -tt
""" sms.py (c) 2013 Matthew J Ernisse <mernisse@ub3rgeek.net>
Implement a SMS interface using the Twilio Web API to send people messages.

"""

import core
import re
import urllib2

from botlogger import *
from twilio.rest import TwilioRestClient

import private

TWILIO_ACCOUNT_SID = private.TWILIO_ACCOUNT_SID
TWILIO_ACCOUNT_SECRET = private.TWILIO_ACCOUNT_SECRET
TWILIO_PHONE_NUM = private.TWILIO_ACCOUNT_SECRET

def twiliosend(d, m):
	''' Send an SMS via Twilio'''
	global TWILIO_ACCOUNT_SID, TWILIO_ACCOUNT_SECRET, TWILIO_PHONE_NUM

	client = TwilioRestClient(TWILIO_ACCOUNT_SID, TWILIO_ACCOUNT_SECRET)
	message = client.sms.messages.create(
		body = m,
		to = d,
		from_ = TWILIO_PHONE_NUM)

	log('SMS sent to %s as %s' % (d, message.sid))

def privmsg(self, user, channel, msg):
	speaker = user.split('!', 1)[0]
	dst = speaker
	if channel != self.nickname:
		msg = self._forMe(msg)
		if not msg:
			return

		dst = channel

	matches = re.search(r'^(poke|sms)\s+(\S+)\s+(.*)$', msg, re.I)
	if not matches:
		return

	target = matches.group(2)
	message = matches.group(3)

	# save header so we can programatically determine length later.
	header = "<%s on behalf of %s> " % (self.nickname, speaker)
	message = header + message

	if len(message) > 160:
		self.msg(dst, 'Sorry, message over %i characters.' % (
			160 - len(header)
		), only=True)

	if not re.search(r'^\+?\d+[ .(-]?\d+[ .)-]?\d+$', target):
		# doesn't look like a phone number, try to map it.
		b = core.brain.getfor(target, 'MOBILE')
		if not b:
			self.msg(dst,
				'Could not find phone number for %s' % target,
				only=True)

		target = b

	try:
		twiliosend(target, message)
	except Exception, e:
		self.msg(dst, 'Unable to SMS %s: %s' % (target, str(e)))
		log('Unable to SMS from %s to %s, msg=%s, err=%s' % (
			speaker, target, message, str(e)
		))
		raise core.StopCallBacks

	self.msg(dst, 'SMS sent to %s.' % target, only=True)

core.register_module(__name__)
