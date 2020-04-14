# -*- coding: utf-8 -*-
from .. import html5

class DeferredCall( object ):
	"""
		Calls the given function with a fixed delay.
		This allows assuming that calls to NetworkService are always
		asynchronous, so its guaranteed that any initialization code can run
		before the Network-Call yields results.
	"""
	def __init__( self, func, *args, **kwargs ):
		"""
			:param func: Callback function
			:type func: Callable
		"""
		super( DeferredCall, self ).__init__()
		delay = 25
		self._callback = None

		if "_delay" in kwargs.keys():
			delay = kwargs["_delay"]
			del kwargs["_delay"]

		if "_callback" in kwargs.keys():
			self._callback = kwargs["_callback"]
			del kwargs["_callback"]

		self._tFunc = func
		self._tArgs = args
		self._tKwArgs = kwargs
		html5.window.setTimeout(self.run, delay)

	def run(self):
		"""
			Internal callback that executes the callback function
		"""
		self._tFunc( *self._tArgs, **self._tKwArgs )
		if self._callback:
			self._callback(self)
