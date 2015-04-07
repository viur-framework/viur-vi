#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class StartupQueue( object ):
	def __init__(self):
		super(StartupQueue, self).__init__()
		self.isRunning = False
		self.q = []
		self.currentElem = -1
		self.finalElem = None

	def setFinalElem(self, elem):
		assert self.finalElem is None
		assert not self.isRunning
		self.finalElem = elem

	def insertElem(self, priority, elem):
		assert not self.isRunning
		self.q.append( (priority,elem) )

	def run(self):
		assert not self.isRunning
		assert self.finalElem is not None
		self.isRunning = True
		self.next()

	def next(self):
		self.currentElem += 1
		if self.currentElem < len( self.q ): #This index is still valid
			cb = self.q[self.currentElem][1]
			print("Running startup callback #%s" % str(self.currentElem))
			cb()
		elif self.currentElem == len( self.q ): #We should call the final element
			self.finalElem()
		else:
			raise RuntimeError("StartupQueue has no more elements to call. Someone called next() twice!")

startupQueue = StartupQueue()

class PriorityQueue( object ):
	def __init__( self ):
		super( PriorityQueue, self ).__init__()
		self._q = {}
	
	def insert( self, priority, validateFunc, generator ):
		priority = int( priority )
		if not priority in self._q.keys():
			self._q[ priority ] = []
		self._q[ priority ].append( (validateFunc, generator) )
	
	def select( self, *args, **kwargs ):
		prios = list( self._q.keys() )
		prios.sort( reverse=True )
		for p in prios:
			for validateFunc, generator in self._q[ p ]:
				if validateFunc( *args, **kwargs ):
					return( generator )


HandlerClassSelector = PriorityQueue() # Used during startup to select an Wrapper-Class
editBoneSelector = PriorityQueue() # Queried by editWidget to locate its bones
actionDelegateSelector = PriorityQueue() # Locates an action for a given module/action-name
displayDelegateSelector = PriorityQueue() # Selects a widget used to display data from a certain modul
initialHashHandler = PriorityQueue() # Provides the handler for the initial hash given in the url
extendedSearchWidgetSelector = PriorityQueue() # Selects a widget used to perform user-customizable searches
extractorDelegateSelector = PriorityQueue() # selects a widget used to extract raw data from bones including special features like multilanguage support
toplevelActionSelector = PriorityQueue() # Top bar actions queue

#OLD
viewDelegateSelector = PriorityQueue() # Queried by listWidget to determine the viewDelegates for the table
protocolWrapperClassSelector = PriorityQueue() # Used during startup to select an Wrapper-Class
protocolWrapperInstanceSelector = PriorityQueue() # Used afterwards to get a specific instance

