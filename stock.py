''' stock.py (c) 2014 - 2021 Matthew J. Ernisse <matt@going-flying.com>

Emit stock information from the Yahoo API (uses yahoo_fin on pypi)

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
import re

from botlogger import *
from yahoo_fin import stock_info

def fetch_quote(symbol):
	curr = stock_info.get_quote_data(symbol)
	mc = format_thousands(curr['marketCap'])

	return (f'{curr["longName"]}: ${curr["regularMarketPrice"]:0,.02f} '
		f'({curr["regularMarketChange"]:0.02f} '
		f'{curr["regularMarketChangePercent"]:0.02f}% '
		f'Cap {mc})')


def format_thousands(num):
	suffix = ['', 'K$', 'MM$', 'BN$', 'TN$']
	i = 0

	while num / 1000 > 1.0:
		i += 1
		num /= 1000

	return f'{num:0,.04f} {suffix[i]}'


def privmsg(self, user, channel, msg):
	dst = user.split('!', 1)[0]
	if channel != self.nickname:
		msg = self._forMe(msg)
		if not msg:
			return

		dst = channel

	matches = re.search(
		r'^ticker:?\s+([a-z0-9_.-^]+)\s*$',
		msg,
		re.I
	)

	if not matches:
		return

	symbol = matches.group(1).lower()
	try:
		msg = fetch_quote(symbol)

	except Exception as e:
		log(f'stock() failed to fetch symbol {symbol}, {e!s}')
		self.msg(dst, "Failed to fetch symbol data.")
		return

	self.msg(dst, msg, only=True)



core.register_module(__name__)
