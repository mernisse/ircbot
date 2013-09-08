# Copyright (c) 1989, 1993
#	The Regents of the University of California.  All rights reserved.
#
# This code is derived from software posted to USENET.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. Neither the name of the University nor the names of its contributors
#    may be used to endorse or promote products derived from this software
#    without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
#
# Phase of the Moon.  Calculates the current phase of the moon.
#  Based on routines from `Practical Astronomy with Your Calculator',
#  by Duffett-Smith.  Comments give the section from the book that
#  particular piece of code was adapted from.
# 
# -- Keith E. Brandt  VIII 1984
#
# Updated to the Third Edition of Duffett-Smith's book, IX 1998

# Adapted from 
# $OpenBSD: pom.c,v 1.12 2005/11/05 21:25:00 jmc Exp $ by mernisse

from math import sin, cos
from time import gmtime

# Solar orbit characteristics
EPOCH = 1990			# Astronomical EPOCH
EPSILONg = 279.403303		# solar ecliptic longitude at EPOCH
RHOg = 282.768422		# solar ecliptic longitude of perigee at EPOCH
ECCEN = 0.016713		# solar orbit eccentricity at EPOCH

# Lunar orbit characteristics
LZERO = 318.351648		# lunar mean longitude at EPOCH
PZERO = 36.340410		# lunar mean longitude of perigee at EPOCH
NZERO = 318.510107		# lunar mean longitude of node at EPOCH

# Pi...ish
PI = 3.14159265358979323846

def potm(time_t):
	"""Phase Of The Moon - takes a list/tuple of locatime values
	as input, returns percentage of illumination of the
	moon's visible disc."""

	# 0=year, 1=mon,  2=mday, 3=hour, 4=min, 5=sec, 6=wday, 7=yday, 8=dst
	# python is not perl, we don't need frickery.
	days = (time_t[7]) + ((time_t[3] + (time_t[4] / 60.0)
	+ (time_t[5] / 3600.0)) / 24)


	(N, Msol, Ec, LambdaSol, l, Mm, Ev, Ac, A3, Mmprime) = ('','','','','','','','','','')
	(A4, lprime, V, ldprime, D, Nm) = ('','','','','','')

	cnt = EPOCH
	while cnt < time_t[0]:
		if isleap(cnt):
			days = days + 366;
		else: 
			days = days + 365;
		cnt = cnt + 1

	# From potm() in pom.c

	N = adj360(360.0 * days / 365.242191)		# sec 46 #3
	Msol = adj360(N + EPSILONg - RHOg)		# sec 46 #4
	Ec = 360 / PI * ECCEN * sin(dtor(Msol))		# sec 46 #5
	LambdaSol = N + Ec + EPSILONg			# sec 46 #6
	LambdaSol = adj360(LambdaSol)

	l = adj360(13.1763966 * days + LZERO)		# sec 65 #4
	Mm = adj360(l - (0.1114041 * days) - PZERO)	# sec 65 #5
	Nm = adj360(NZERO - (0.0529539 * days))		# sec 65 #6
	Ev = 1.2739 * sin(dtor(2*(l - LambdaSol) - Mm))	# sec 65 #7
	Ac = 0.1858 * sin(dtor(Msol))			# sec 65 #8
	A3 = 0.37 * sin(dtor(Msol))				
	Mmprime = Mm + Ev - Ac - A3			# sec 65 #9
	Ec = 6.2886 * sin(dtor(Mmprime))		# sec 65 #10
	A4 = 0.214 * sin(dtor(2 * Mmprime))		# sec 65 #11
	lprime = l + Ev + Ec - Ac + A4			# sec 65 #12
	V = 0.6583 * sin(dtor(2 * (lprime - LambdaSol)))	# sec 65 #13
	ldprime = lprime + V				# sec 65 #14
	D = ldprime - LambdaSol				# sec 67 #2

	return 50.0 * (1 - cos(dtor(D)))		# sec 67 #3

def isleap(year):
	"""Is the input year a leap year.  Adapted from
	The C Programming Language, Second Edition
	by Brian W. Kernighan and Dennis M. Ritchie."""

	if ( ((year % 4 == 0) and (year % 100 != 0)) or (year % 400 == 0) ):
		return 1

	return None

def adj360(deg): 
	"""take a number and make it 0 <= deg <= 360"""

	while True:
		if deg < 0.0:
			deg = deg + 360.0
		elif deg > 360.0:
			deg = deg - 360.0
		else:
			return deg

def dtor(deg):
	"""Degrees to Radians (ish)"""

	return (deg * PI / 180)

def pom():
	"""return the integer value of potm"""

	return int(potm(gmtime()))
