#!/usr/bin/env python3
# -*- coding: utf-8 -*-


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
#OLD


viewDelegateSelector = PriorityQueue() # Queried by listWidget to determine the viewDelegates for the table
actionDelegateSelector = PriorityQueue() # Locates an QAction for a given modul/action-name
protocolWrapperClassSelector = PriorityQueue() # Used during startup to select an Wrapper-Class
protocolWrapperInstanceSelector = PriorityQueue() # Used afterwards to get a specific instance

