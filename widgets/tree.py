import pyjd # this is dummy in pyjs.
from pyjamas.ui.RootPanel import RootPanel
from pyjamas.ui.Button import Button
from pyjamas.ui.HTML import HTML
from pyjamas.ui.Label import Label
from pyjamas.ui import Event
from pyjamas import Window
from pyjamas.HTTPRequest import HTTPRequest
from pyjamas.ui.FocusWidget import FocusWidget
from pyjamas.ui.Widget import Widget
from pyjamas.ui.Panel import Panel
from pyjamas import DOM
import json
from network import NetworkService
from priorityqueue import viewDelegateSelector
from widgets.table import DataTable
from widgets.actionbar import ActionBar

import pygwt


class NodeWidget( Widget ):
	def __init__(self, modul, data, *args, **kwargs ):
		self.element = DOM.createElement("div")
		super( NodeWidget, self ).__init__( *args, **kwargs )
		self.modul = modul
		self.data = data
		self.element.innerHTML = data["name"]
		DOM.setStyleAttribute( self.getElement(), "border","1px solid blue")


class LeafWidget( Widget ):
	def __init__(self, modul, data, *args, **kwargs ):
		self.element = DOM.createElement("div")
		super( LeafWidget, self ).__init__( *args, **kwargs )
		self.modul = modul
		self.data = data
		self.element.innerHTML = data["name"]
		DOM.setStyleAttribute( self.getElement(), "border","1px solid black")

class TreeWidget( Widget ):
	def __init__( self, modul, rootNode=None, node=None, *args, **kwargs ):
		"""
			@param modul: Name of the modul we shall handle. Must be a list application!
			@type modul: string
		"""
		self.element = DOM.createElement("div")
		super( TreeWidget, self ).__init__( self.element )
		self.modul = modul
		self.rootNode = rootNode
		self.node = node or rootNode
		#self.setStyleName("vi_viewer")
		#self.actionBar = ActionBar( self, modul )
		#DOM.appendChild( self.element, self.actionBar.getElement() )
		#self.actionBar.onAttach()
		self.pathList = DOM.createElement("div")
		DOM.appendChild( self.getElement(), self.pathList )
		DOM.setStyleAttribute(self.pathList,"border","1px solid red")
		self.entryFrame = DOM.createElement("div")
		DOM.appendChild( self.getElement(), self.entryFrame )
		DOM.setStyleAttribute(self.entryFrame,"border","1px solid green")
		self._currentCursor = None
		self._currentRequests = []
		if self.rootNode:
			self.reloadData()
		else:
			NetworkService.request(self.modul,"listRootNodes", successHandler=self.onSetDefaultRootNode)
		self.children = []
		self.path = []
		self.pathChildren = []
		self.sinkEvents( Event.ONCLICK )
		##Proxy some events and functions of the original table
		#for f in ["selectionChangedEvent","selectionActivatedEvent","cursorMovedEvent","getCurrentSelection"]:
		#	setattr( self, f, getattr(self.table,f))
		#self.actionBar.setActions(["add","edit","delete"])
		#HTTPRequest().asyncGet("/admin/%s/list" % self.modul, self)


	def onBrowserEvent(self, event):
		super( TreeWidget, self ).onBrowserEvent( event )
		eventType = DOM.eventGetType(event)
		if eventType == "click":
			for c in self.children:
				# Test if the user clicked a node/leaf item
				if c.getElement() == event.target:
					if isinstance( c, NodeWidget ):
						self.path.append( c.data )
						self.rebuildPath()
						self.setNode( c.data["id"] )
						return
			for c in self.pathChildren:
				# Test if the user clicked inside the path-list
				if c.getElement() == event.target:
					self.path = self.path[ : self.pathChildren.index( c )]
					self.rebuildPath()
					self.setNode( c.data["id"] )
					return
		print( eventType )

	def onSetDefaultRootNode(self, req):
		data = NetworkService.decode( req )
		if len(data)>0:
			self.setRootNode( data[0]["key"])

	def setRootNode(self, rootNode):
		self.rootNode = rootNode
		self.node = rootNode
		self.reloadData()

	def setNode(self, node):
		self.node = node
		self.reloadData()

	def rebuildPath(self):
		for c in self.pathChildren[:]:
			c.onDetach()
			DOM.removeChild( self.pathList, c.getElement() )
			self.pathChildren.remove( c )
		for p in [None]+self.path:
			if p is None:
				c = NodeWidget( self.modul, {"id":self.rootNode,"name":"root"} )
			else:
				c = NodeWidget( self.modul, p )
			self.pathChildren.append( c )
			DOM.appendChild( self.pathList, c.getElement() )
			c.onAttach()

	def reloadData(self):
		assert self.node is not None, "reloadData called while self.node is None"
		for c in self.children[:]:
			self.removeItem( c )
		r = NetworkService.request(self.modul,"list/node", {"node":self.node}, successHandler=self.onRequestSucceded )
		r.reqType = "node"
		r = NetworkService.request(self.modul,"list/leaf", {"node":self.node}, successHandler=self.onRequestSucceded )
		r.reqType = "leaf"

	def onRequestSucceded(self, req):
		data = NetworkService.decode( req )
		for skel in data["skellist"]:
			if req.reqType=="node":
				n = NodeWidget( self.modul, skel )
			else:
				n = LeafWidget( self.modul, skel )
			self.addItem( n )

	def addItem(self, item):
		self.children.append(item)
		DOM.appendChild( self.entryFrame, item.getElement() )
		item.onAttach()

	def removeItem( self, item ):
		item.onDetach()
		DOM.removeChild( self.entryFrame, item.getElement() )
		self.children.remove( item )
