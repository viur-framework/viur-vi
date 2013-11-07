import html5
import pyjd # this is dummy in pyjs.
from network import NetworkService
from widgets import ActionBar
from event import EventDispatcher


class NodeWidget( html5.Div ):
	def __init__(self, modul, data, *args, **kwargs ):
		super( NodeWidget, self ).__init__( *args, **kwargs )
		self.modul = modul
		self.data = data
		self.element.innerHTML = data["name"]
		self["style"]["border"] = "1px solid blue"
		self["class"] = "tree treeitem node"


class LeafWidget( html5.Div ):
	def __init__(self, modul, data, *args, **kwargs ):
		super( LeafWidget, self ).__init__( *args, **kwargs )
		self.modul = modul
		self.data = data
		self.element.innerHTML = data["name"]
		self["style"]["border"] = "1px solid black"
		self["class"] = "tree treeitem leaf"

class FileWidget( LeafWidget ):
	def __init__(self, modul, data, *args, **kwargs ):
		super( FileWidget, self ).__init__( modul, data, *args, **kwargs )
		if "servingurl" in data.keys():
			self.appendChild( html5.Img( data["servingurl"]) )
		self["class"].append("file")

def doesEventHitWidget( event, widget ):
	while widget:
		if event.target == widget.element:
			return( True )
		widget = widget.parent()
	return( False )

class SelectableDiv( html5.Div ):
	"""
		Provides a Container, which allows selecting its contents.
		Designed to be used within a tree widget, as it distinguishes between
		two different types of content (nodes and leafs) and allows selections to
		be restricted to a certain kind.
	"""


	def __init__(self, nodeWidget, leafWidget, selectionType="both", multiSelection=False, *args, **kwargs ):
		super( SelectableDiv, self ).__init__(*args, **kwargs)
		self["class"].append("tree selectioncontainer")
		self["tabindex"] = 1
		self.selectionType = selectionType
		self.multiSelection = multiSelection
		self.nodeWidget = nodeWidget
		self.leafWidget = leafWidget
		self.selectionChangedEvent = EventDispatcher("selectionChanged")
		self.selectionActivatedEvent = EventDispatcher("selectionActivated")
		self.cursorMovedEvent = EventDispatcher("cursorMoved")
		self._selectedItems = [] # List of row-indexes currently selected
		self._currentItem = None # Rowindex of the cursor row
		self._isMouseDown = False # Tracks status of the left mouse button
		self._isCtlPressed = False # Tracks status of the ctrl key
		self._ctlStartRow = None # Stores the row where a multi-selection (using the ctrl key) started
		self.sinkEvent( "onClick","onDblClick", "onMouseMove", "onMouseDown", "onMouseUp", "onKeyDown", "onKeyUp" )

	def setCurrentItem(self, item):
		if self._currentItem:
			self._currentItem["class"].remove("cursor")
		self._currentItem = item
		if item:
			item["class"].append("cursor")

	def onClick(self, event):
		self.focus()
		for child in self._children:
			if doesEventHitWidget( event, child ):
				self.setCurrentItem( child )
				if self._isCtlPressed:
					self.addSelectedItem( child )
		if not self._isCtlPressed:
			self.clearSelection()

	def onDblClick(self, event):
		print("DBLCLICK")
		for child in self._children:
			if doesEventHitWidget( event, child ):
				if self.selectionType=="node" and isinstance( child, self.nodeWidget ) or \
				   self.selectionType=="leaf" and isinstance( child, self.leafWidget ) or \
				   self.selectionType=="both":
					self.selectionActivatedEvent.fire( self, [child] )

	def onKeyDown(self, event):
		print("GOT KEY DOWN")
		if event.keyCode==13: # Return
			if len( self._selectedItems )>0:
				self.selectionActivatedEvent.fire( self, self._selectedItems )
				event.preventDefault()
				return
			if self._currentItem is not None:
				self.selectionActivatedEvent.fire( self, [self._currentItem] )
				event.preventDefault()
				return
		elif event.keyCode==17: #Ctrl
			self._isCtlPressed = True

	def onKeyUp(self, event):
		if event.keyCode==17:
			self._isCtlPressed = False

	def clearSelection(self):
		for child in self._children[:]:
			self.removeSelectedItem( child )

	def addSelectedItem(self, item):
		#if not self.multiSelection:
		#	return
		if self.selectionType=="node" and isinstance( item, self.nodeWidget ) or \
		   self.selectionType=="leaf" and isinstance( item, self.leafWidget ) or \
		   self.selectionType=="both":
			if not item in self._selectedItems:
				self._selectedItems.append( item )
				item["class"].append("selected")

	def removeSelectedItem(self,item):
		if not item in self._selectedItems:
			return
		self._selectedItems.remove( item )
		item["class"].remove("selected")

	def clear(self):
		self.clearSelection()
		for child in self._children[:]:
			self.removeChild( child )

	def getCurrentSelection(self):
		if len(self._selectedItems)>0:
			return( self._selectedItems[:] )
		if self._currentItem:
			return( self._currentItem )
		return( None )

class TreeWidget( html5.Div ):

	nodeWidget = NodeWidget
	leafWidget = FileWidget

	def __init__( self, modul, rootNode=None, node=None, *args, **kwargs ):
		"""
			@param modul: Name of the modul we shall handle. Must be a list application!
			@type modul: string
		"""
		super( TreeWidget, self ).__init__( )
		print("INIT TREE WIDGET")
		self.modul = modul
		self.rootNode = rootNode
		self.node = node or rootNode
		self.actionBar = ActionBar( modul, "tree" )
		self.appendChild( self.actionBar )
		self.pathList = html5.Div()
		self.appendChild( self.pathList )
		self.entryFrame = SelectableDiv( self.nodeWidget, self.leafWidget )
		self.appendChild( self.entryFrame )
		self.entryFrame.selectionActivatedEvent.register( self )
		self._currentCursor = None
		self._currentRequests = []
		if self.rootNode:
			print("INIT TREE WIDGET X!")
			self.reloadData()
		else:
			print("INIT TREE WIDGET X2")
			NetworkService.request(self.modul,"listRootNodes", successHandler=self.onSetDefaultRootNode)
		self.path = []
		self.sinkEvent( "onClick" )
		#Proxy some events and functions of the original table
		for f in ["selectionChangedEvent","selectionActivatedEvent","cursorMovedEvent","getCurrentSelection"]:
			setattr( self, f, getattr(self.entryFrame,f))
		self.actionBar.setActions(["add","edit","delete"])

	def onSelectionActivated(self, div, selection ):
		if len(selection)!=1:
			return
		item = selection[0]
		if isinstance( item, self.nodeWidget ):
			self.path.append( item.data )
			self.rebuildPath()
			self.setNode( item.data["id"] )
		elif isinstance(item, self.leafWidget):
			print("SELECTED LEAF")

	def onClick(self, event):
		print("ONCLICK")
		super( TreeWidget, self ).onClick( event )
		for c in self.pathList._children:
			# Test if the user clicked inside the path-list
			if doesEventHitWidget( event, c ):
				self.path = self.path[ : self.pathList._children.index( c )]
				self.rebuildPath()
				self.setNode( c.data["id"] )
				return

	def onSetDefaultRootNode(self, req):
		data = NetworkService.decode( req )
		if len(data)>0:
			self.setRootNode( data[0]["key"])

	def setRootNode(self, rootNode):
		self.rootNode = rootNode
		self.node = rootNode
		self.rebuildPath()
		self.reloadData()

	def setNode(self, node):
		self.node = node
		self.reloadData()

	def rebuildPath(self):
		for c in self.pathList._children[:]:
			self.pathList.removeChild( c )
		for p in [None]+self.path:
			if p is None:
				c = NodeWidget( self.modul, {"id":self.rootNode,"name":"root"} )
			else:
				c = NodeWidget( self.modul, p )
			self.pathList.appendChild( c )
			#DOM.appendChild( self.pathList, c.getElement() )
			#c.onAttach()

	def reloadData(self):
		assert self.node is not None, "reloadData called while self.node is None"
		self.entryFrame.clear()
		r = NetworkService.request(self.modul,"list/node", {"node":self.node}, successHandler=self.onRequestSucceded )
		r.reqType = "node"
		r = NetworkService.request(self.modul,"list/leaf", {"node":self.node}, successHandler=self.onRequestSucceded )
		r.reqType = "leaf"

	def onRequestSucceded(self, req):
		data = NetworkService.decode( req )
		for skel in data["skellist"]:
			if req.reqType=="node":
				n = self.nodeWidget( self.modul, skel )
			else:
				n = self.leafWidget( self.modul, skel )
			self.entryFrame.appendChild(n)


