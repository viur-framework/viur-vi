import html5
import pyjd # this is dummy in pyjs.
from network import NetworkService
from widgets.actionbar import ActionBar
from event import EventDispatcher
from priorityqueue import displayDelegateSelector, viewDelegateSelector
import utils


class NodeWidget( html5.Div ):
	def __init__(self, modul, data, structure, *args, **kwargs ):
		super( NodeWidget, self ).__init__( *args, **kwargs )
		self.modul = modul
		self.data = data
		self.structure = structure
		self.rebuildDescription()
		self["style"]["border"] = "1px solid blue"
		self["class"] = "treeitem node supports_drag supports_drop"
		self["draggable"] = True
		self.sinkEvent("onDragOver","onDrop","onDragStart")

	def rebuildDescription(self):
		hasDescr = False
		for boneName, boneInfo in self.structure:
			if "params" in boneInfo.keys() and isinstance(boneInfo["params"], dict):
				params = boneInfo["params"]
				if "frontend_default_visible" in params.keys() and params["frontend_default_visible"]:
					wdg = viewDelegateSelector.select( self.modul, boneName, utils.boneListToDict(self.structure) )
					if wdg is not None:
						self.appendChild( wdg(self.modul, boneName, utils.boneListToDict(self.structure) ).render( self.data, boneName ))
						hasDescr = True
		if not hasDescr:
			self.appendChild( html5.TextNode( self.data["name"]))

	def onDragOver(self, event):
		try:
			nodeType, srcKey = event.dataTransfer.getData("Text").split("/")
		except:
			return
		event.preventDefault()
		event.stopPropagation()

	def onDragStart(self, event):
		print("DRAG START")
		event.dataTransfer.setData( "Text", "node/"+self.data["id"] )
		event.stopPropagation()

	def onDrop(self, event):
		try:
			nodeType, srcKey = event.dataTransfer.getData("Text").split("/")
		except:
			return
		NetworkService.request(self.modul,"move",{"skelType": nodeType, "id":srcKey, "destNode": self.data["id"]}, modifies=True, secure=True)
		event.preventDefault()
		event.stopPropagation()



class LeafWidget( html5.Div ):
	def __init__(self, modul, data, structure, *args, **kwargs ):
		super( LeafWidget, self ).__init__( *args, **kwargs )
		self.modul = modul
		self.data = data
		self.structure = structure
		self.rebuildDescription()
		self.element.innerHTML = data["name"]
		self["style"]["border"] = "1px solid black"
		self["class"] = "treeitem leaf supports_drag"
		self["draggable"] = True
		self.sinkEvent("onDragStart")

	def rebuildDescription(self):
		hasDescr = False
		for boneName, boneInfo in self.structure:
			if "params" in boneInfo.keys() and isinstance(boneInfo["params"], dict):
				params = boneInfo["params"]
				if "frontend_default_visible" in params.keys() and params["frontend_default_visible"]:
					wdg = viewDelegateSelector.select( self.modul, boneName, utils.boneListToDict(self.structure) )
					if wdg is not None:
						self.appendChild( wdg(self.modul, boneName, utils.boneListToDict(self.structure) ).render( self.data, boneName ))
						hasDescr = True
		if not hasDescr:
			self.appendChild( html5.TextNode( self.data["name"]))

	def onDragStart(self, event):
		print("DRAG START")
		event.dataTransfer.setData( "Text", "leaf/"+self.data["id"] )
		event.stopPropagation()

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
		self["class"].append("selectioncontainer")
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
			return( [self._currentItem] )
		return( None )

class TreeWidget( html5.Div ):

	nodeWidget = NodeWidget
	leafWidget = LeafWidget
	defaultActions = ["add.node", "add.leaf", "edit", "delete"]

	def __init__( self, modul, rootNode=None, node=None, *args, **kwargs ):
		"""
			@param modul: Name of the modul we shall handle. Must be a list application!
			@type modul: string
		"""
		super( TreeWidget, self ).__init__( )
		self["class"].append("tree")
		print("INIT TREE WIDGET")
		self.modul = modul
		self.rootNode = rootNode
		self.node = node or rootNode
		self.actionBar = ActionBar( modul, "tree" )
		self.appendChild( self.actionBar )
		self.pathList = html5.Div()
		self.pathList["class"].append("breadcrumb")
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
		self.actionBar.setActions( self.defaultActions )

	def onAttach(self):
		super( TreeWidget, self ).onAttach()
		NetworkService.registerChangeListener( self )

	def onDetach(self):
		super( TreeWidget, self ).onDetach()
		NetworkService.removeChangeListener( self )


	def onDataChanged(self, modul):
		if modul!=self.modul:
			return
		self.reloadData()

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
				c = NodeWidget( self.modul, {"id":self.rootNode,"name":"root"}, [] )
			else:
				c = NodeWidget( self.modul, p, [] )
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
				n = self.nodeWidget( self.modul, skel, data["structure"] )
			else:
				n = self.leafWidget( self.modul, skel, data["structure"] )
			self.entryFrame.appendChild(n)


	@staticmethod
	def canHandle( modul, modulInfo ):
		print("CANHANDLE", modul, modulInfo)
		return( modulInfo["handler"].startswith("tree." ) )

displayDelegateSelector.insert( 1, TreeWidget.canHandle, TreeWidget )