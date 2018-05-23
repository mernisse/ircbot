#!/usr/bin/python -tt
''' core.py - (c) 2009, 2013 Matthew John Ernisse <mernisse@ub3rgeek.net>
provide core functions for the bot

The MODULES list holds all the names for the plugins registered to the
bot.  Each plugin should import core and call core.register_module(__name__)
to ensure it is present in this list.  Failure to do so will cause the
callbacks to never get processed.

This could be useful if you want to extend parts of the bot but not register
callbacks.

'''
import pickle
from botlogger import *

class Brain(dict):
	''' Implement a simple persistant key, value storage object.  This 
	saves state by overloading __setitem__ and __delitem__ to pickle the
	object to disk and __init__ to load the object from disk.

	The file to pickle to/from is stored as the fn attribute.

	'''
	fn = 'mybrain.pkl'

	def __init__(self, **kwargs):
		''' create a new Brain.  If a mapping is specified with the
		constructor then it OVERWRITES any existing saved state.

		'''
		self._load()
		super(Brain, self).__init__(**kwargs)

	def _load(self):
		''' Load the object from disk '''
		if not os.path.exists(self.fn):
			return

		fd = open(self.fn, 'r')

		selfie = pickle.load(fd)
		fd.close()

		for k,v in selfie.iteritems():
			log('loaded %i items for %s' % (len(v), k))
			super(Brain, self).__setitem__(k, v)

	def _save(self):
		''' Save the object to disk '''
		try:
			fd = open(self.fn, 'wb')
			pickle.dump(self, fd)
			fd.flush()
			fd.close()
		except IOError, e:
			log('failed to write brain, ioerror: %s' % str(e))

		log('wrote brain to disk')

	def __delitem__(self, k):
		''' B.__delitem__(k) <==> del B[k] '''
		super(Brain, self).__delitem__(k)

		self._save()

	def __setitem__(self, k, v):
		''' B.__setitem__(k, v) <==> B[k] = v '''
		super(Brain, self).__setitem__(k, v)

		self._save()

	def getfor(self, who, k, default=None):
		''' B.getfor(w,k[,d]) -> B[w][k] if k in w and w in B else d.'''
		try:
			return self[who][k]
		except KeyError:
			return default
