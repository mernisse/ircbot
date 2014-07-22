__all__ = ["core", "youtube"]

import sys

from . import *

def processurl(speaker, url):
	''' Meta-function for calling all the processurl functions in
	the module

	'''
	for mod in __all__:
		mod = ".".join([__name__, mod])

		if getattr(sys.modules[mod], 'processurl', None):
			url = sys.modules[mod].processurl(speaker, url)

	return url
