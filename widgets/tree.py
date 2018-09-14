import html5
import pyjd # this is dummy in pyjs.
from network import NetworkService
from widgets.actionbar import ActionBar
from widgets.search import Search
from event import EventDispatcher
from priorityqueue import displayDelegateSelector, viewDelegateSelector, moduleHandlerSelector
import utils
from html5.keycodes import *
from config import conf

class NodeWidget( html5.Div ):
	"""
		Displays one Node (ie a directory) inside a TreeWidget
	"""
	def __init__(self, modul, data, structure, *args, **kwargs ):
		"""
			@param modul: Name of the modul for which we'll display data
			@type modul: String
			@param data: The data we're going to display
			@type data: Dict
			@param structure: The structure of that data as received from server
			@type structure: List
		"""
		super( NodeWidget, self ).__init__( *args, **kwargs )
		self.module = modul
		self.data = data
		self.structure = structure
		self.buildDescription()
		self["class"] = "treeitem node supports_drag supports_drop"
		self["draggable"] = True
		self.sinkEvent("onDragOver","onDrop","onDragStart", "onDragLeave")

	def buildDescription(self):
		"""
			Creates the visual representation of our entry
		"""
		hasDescr = False
		for boneName, boneInfo in self.structure:
			if "params" in boneInfo.keys() and isinstance(boneInfo["params"], dict):
				params = boneInfo["params"]
				if "frontend_default_visible" in params.keys() and params["frontend_default_visible"]:

					structure = {k: v for k, v in self.structure}
					wdg = viewDelegateSelector.select(self.module, boneName, structure)

					if wdg is not None:
						self.appendChild(wdg(self.module, boneName, structure).render(self.data, boneName))
						hasDescr = True
		if not hasDescr:
			self.appendChild( html5.TextNode( self.data["name"]))

	def onDragOver(self, event):
		"""
			Check if we can handle the drag-data
		"""
		if not "insert_here" in self["class"]:
			self["class"].append("insert_here")
		try:
			nodeType, srcKey = event.dataTransfer.getData("Text").split("/")
		except:
			return( super(NodeWidget,self).onDragOver(event) )
		event.preventDefault()
		event.stopPropagation()

	def onDragLeave(self, event):
		if "insert_here" in self["class"]:
			self["class"].remove("insert_here")
		return( super(NodeWidget, self).onDragLeave(event))

	def onDragStart(self, event):
		"""
			Store our information in the drag's dataTransfer object
		"""
		event.dataTransfer.setData( "Text", "node/"+self.data["key"] )
		event.stopPropagation()

	def onDrop(self, event):
		"""
			Check if we can handle that drop and make the entries direct children of this node
		"""
		try:
			nodeType, srcKey = event.dataTransfer.getData("Text").split("/")
		except:
			return
		NetworkService.request(self.module,"move",{"skelType": nodeType, "key":srcKey, "destNode": self.data["key"]}, modifies=True, secure=True)
		event.preventDefault()
		event.stopPropagation()



class LeafWidget( html5.Div ):
	"""
		Displays one Node (ie a file) inside a TreeWidget
	"""
	def __init__(self, module, data, structure, *args, **kwargs ):
		"""
			@param module: Name of the modul for which we'll display data
			@type module: String
			@param data: The data we're going to display
			@type data: Dict
			@param structure: The structure of that data as received from server
			@type structure: List
		"""
		super( LeafWidget, self ).__init__( *args, **kwargs )
		self.module = module
		self.data = data
		self.structure = structure
		self.buildDescription()
		self["class"] = "treeitem leaf supports_drag"
		self["draggable"] = True
		self.sinkEvent("onDragStart")

	def buildDescription(self):
		"""
			Creates the visual representation of our entry
		"""
		hasDescr = False
		for boneName, boneInfo in self.structure:
			if "params" in boneInfo.keys() and isinstance(boneInfo["params"], dict):
				params = boneInfo["params"]
				if "frontend_default_visible" in params.keys() and params["frontend_default_visible"]:

					structure = {k: v for k, v in self.structure}
					wdg = viewDelegateSelector.select(self.module, boneName, structure)

					if wdg is not None:
						self.appendChild(wdg(self.module, boneName, structure).render(self.data, boneName))
						hasDescr = True

		if not hasDescr:
			self.appendChild( html5.TextNode( self.data["name"]))

	def onDragStart(self, event):
		"""
			Store our information in the drag's dataTransfer object
		"""
		event.dataTransfer.setData( "Text", "leaf/"+self.data["key"] )
		event.stopPropagation()

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
		self.selectionActivatedEvent = EventDispatcher("selectionActivated") # Double-Click on an currently selected item - ITEM CLICKED !!!!
		self.selectionReturnEvent = EventDispatcher("selectionReturn") # The current selection should be returned to parent widget
		self.cursorMovedEvent = EventDispatcher("cursorMoved")
		self._selectedItems = [] # List of row-indexes currently selected
		self._currentItem = None # Rowindex of the cursor row
		self._isMouseDown = False # Tracks status of the left mouse button
		self._isCtlPressed = False # Tracks status of the ctrl key
		self._ctlStartRow = None # Stores the row where a multi-selection (using the ctrl key) started
		self.sinkEvent( "onClick","onDblClick", "onMouseMove", "onMouseDown", "onMouseUp", "onKeyDown", "onKeyUp" )

	def setCurrentItem(self, item):
		"""
			Sets the  currently selected item (=the cursor) to 'item'
			If there was such an item before, its unselected afterwards.
		"""
		if self._currentItem:
			self._currentItem["class"].remove("cursor")
		self._currentItem = item
		if item:
			item["class"].append("cursor")

	def onClick(self, event):
		self.focus()
		for child in self._children:
			if html5.utils.doesEventHitWidgetOrChildren(event, child):
				self.setCurrentItem( child )
				if self._isCtlPressed:
					self.addSelectedItem( child )
		if not self._isCtlPressed:
			self.clearSelection()
		if self._selectedItems:
			self.selectionChangedEvent.fire( self, self._selectedItems[:])
		elif self._currentItem:
			self.selectionChangedEvent.fire( self, [self._currentItem])
		else:
			self.selectionChangedEvent.fire( self, [])

	def onDblClick(self, event):
		for child in self._children:
			if html5.utils.doesEventHitWidgetOrChildren(event, child):
				if self.selectionType=="node" and isinstance( child, self.nodeWidget ) or \
				   self.selectionType=="leaf" and isinstance( child, self.leafWidget ) or \
				   self.selectionType=="both":
					self.selectionActivatedEvent.fire( self, [child] )

	def activateCurrentSelection(self):
		"""
			Emits the selectionActivated event if there's currently a selection

		"""
		if len( self._selectedItems )>0:
			self.selectionActivatedEvent.fire( self, self._selectedItems )

		elif self._currentItem is not None:
			self.selectionActivatedEvent.fire( self, [self._currentItem] )

	def returnCurrentSelection(self):
		"""
			Emits the selectionReturn event if there's currently a selection

		"""
		selection = []
		if len( self._selectedItems )>0:
			selection = self._selectedItems
			#self.selectionReturnEvent.fire( self, self._selectedItems )
		elif self._currentItem is not None:
			selection = [self._currentItem]
		if self.selectionType=="node":
			selection = [x for x in selection if isinstance(x,self.nodeWidget)]
		elif self.selectionType=="leaf":
			selection = [x for x in selection if isinstance(x,self.leafWidget)]
		self.selectionReturnEvent.fire( self, selection )

	def onKeyDown(self, event):
		if isReturn(event.keyCode): # Return
			self.activateCurrentSelection()
			event.preventDefault()
			return
		elif isSingleSelectionKey(event.keyCode): #Ctrl
			self._isCtlPressed = True

	def onKeyUp(self, event):
		if isSingleSelectionKey(event.keyCode):
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
		self.selectionChangedEvent.fire( self, [] )

	def getCurrentSelection(self):
		if len(self._selectedItems)>0:
			return( self._selectedItems[:] )
		if self._currentItem:
			return( [self._currentItem] )
		return( None )

class TreeWidget( html5.Div ):

	nodeWidget = NodeWidget
	leafWidget = LeafWidget
	defaultActions = ["add.node", "add.leaf", "selectrootnode", "edit", "delete", "reload"]

	def __init__( self, module, rootNode=None, node=None, isSelector=False, *args, **kwargs ):
		"""
			@param modul: Name of the modul we shall handle. Must be a list application!
			@type modul: string
			@param rootNode: The rootNode we shall display. If None, we try to select one.
			@type rootNode: String or None
			@param node: The node we shall display at start. Must be a child of rootNode
			@type node: String or None
		"""
		super( TreeWidget, self ).__init__( )
		self["class"].append("tree")
		self.module = module
		self.rootNode = rootNode
		self.node = node or rootNode
		self.actionBar = ActionBar( module, "tree" )
		self.appendChild( self.actionBar )
		self.pathList = html5.Div()
		self.pathList["class"].append("breadcrumb")
		self.appendChild( self.pathList )
		self.entryFrame = SelectableDiv( self.nodeWidget, self.leafWidget )
		self.appendChild( self.entryFrame )
		self.entryFrame.selectionActivatedEvent.register( self )
		self._batchSize = 99
		self._currentCursor = { "node" : None, "leaf": None }
		self._currentRequests = []
		self.rootNodeChangedEvent = EventDispatcher("rootNodeChanged")
		self.nodeChangedEvent = EventDispatcher("nodeChanged")
		self.isSelector = isSelector
		if self.rootNode:
			self.reloadData()
		else:
			NetworkService.request(self.module,"listRootNodes", successHandler=self.onSetDefaultRootNode)
		self.path = []
		self.sinkEvent( "onClick" )
		#Proxy some events and functions of the original table
		for f in ["selectionChangedEvent","selectionActivatedEvent","cursorMovedEvent","getCurrentSelection", "selectionReturnEvent"]:
			setattr( self, f, getattr(self.entryFrame,f))
		self.actionBar.setActions( self.defaultActions+(["select","close"] if isSelector else []) )

	def showErrorMsg(self, req=None, code=None):
		"""
			Removes all currently visible elements and displayes an error message
		"""
		self.actionBar["style"]["display"] = "none"
		self.entryFrame["style"]["display"] = "none"
		errorDiv = html5.Div()
		errorDiv["class"].append("error_msg")
		if code and (code==401 or code==403):
			txt = "Access denied!"
		else:
			txt = "An unknown error occurred!"
		errorDiv["class"].append("error_code_%s" % (code or 0))
		errorDiv.appendChild( html5.TextNode( txt ) )
		self.appendChild( errorDiv )

	def onAttach(self):
		super( TreeWidget, self ).onAttach()
		NetworkService.registerChangeListener( self )

	def onDetach(self):
		super( TreeWidget, self ).onDetach()
		NetworkService.removeChangeListener( self )


	def onDataChanged(self, module, **kwargs):
		if module != self.module:

			isRootNode = False
			for k, v in conf["modules"].items():
				if (k == module
				    and v.get("handler") == "list"
				    and v.get("rootNodeOf") == self.module):

					isRootNode = True
					break

			if not isRootNode:
				return

		if "selectrootnode" in self.actionBar.widgets.keys():
			self.actionBar.widgets["selectrootnode"].update()

		self.reloadData()

	def onSelectionActivated(self, div, selection ):
		"""
		FIXME: Does this make sense anymore?
		if len(selection)!=1:
			if self.isSelector:
				conf["mainWindow"].removeWidget(self)
			return
		"""
		if not selection:
			return

		item = selection[0]

		if isinstance( item, self.nodeWidget ):
			self.path.append( item.data )
			self.rebuildPath()
			self.setNode( item.data["key"] )

		elif isinstance(item, self.leafWidget) and self.isSelector == "leaf":
			self.returnCurrentSelection()

	def activateCurrentSelection(self):
		return self.entryFrame.activateCurrentSelection()

	def returnCurrentSelection(self):
		conf["mainWindow"].removeWidget(self)
		return self.entryFrame.returnCurrentSelection()

	def onClick(self, event):
		super( TreeWidget, self ).onClick( event )
		for c in self.pathList._children:
			# Test if the user clicked inside the path-list
			if html5.utils.doesEventHitWidgetOrParents(event, c):
				self.path = self.path[ : self.pathList._children.index( c )]
				self.rebuildPath()
				self.setNode( c.data["key"] )
				return

	def onSetDefaultRootNode(self, req):
		data = NetworkService.decode( req )
		if len(data)>0:
			self.setRootNode( data[0]["key"])

	def setRootNode(self, rootNode):
		self.rootNode = rootNode
		self.node = rootNode
		self.rootNodeChangedEvent.fire( rootNode )
		self.rebuildPath()
		self.reloadData()

	def setNode(self, node):
		self.node = node
		self.nodeChangedEvent.fire( node )
		self.reloadData()

	def rebuildPath(self):
		"""
			Rebuild the displayed path-list.
		"""
		for c in self.pathList._children[:]:
			self.pathList.removeChild( c )
		for p in [None]+self.path:
			if p is None:
				c = NodeWidget( self.module, {"key":self.rootNode,"name":"root"}, [] )
				c["class"].append("is_rootnode")
			else:
				c = NodeWidget( self.module, p, [] )
			self.pathList.appendChild( c )
			#DOM.appendChild( self.pathList, c.getElement() )
			#c.onAttach()

	def reloadData(self, paramsOverride=None):
		assert self.node is not None, "reloadData called while self.node is None"
		self.entryFrame.clear()
		self._currentRequests = []
		if paramsOverride:
			params = paramsOverride.copy()
		else:
			params = { "node":self.node }

		if "amount" not in params:
			params[ "amount" ] = self._batchSize

		r = NetworkService.request(self.module,"list/node", params,
		                           successHandler=self.onRequestSucceded,
		                           failureHandler=self.showErrorMsg )
		r.reqType = "node"
		self._currentRequests.append( r )
		r = NetworkService.request(self.module,"list/leaf", params,
		                           successHandler=self.onRequestSucceded,
		                           failureHandler=self.showErrorMsg )
		r.reqType = "leaf"
		self._currentRequests.append( r )

	def onRequestSucceded(self, req):
		if not req in self._currentRequests:
			return
		self._currentRequests.remove( req )
		data = NetworkService.decode( req )
		for skel in data["skellist"]:
			if req.reqType=="node":
				n = self.nodeWidget( self.module, skel, data["structure"] )
			else:
				n = self.leafWidget( self.module, skel, data["structure"] )

			self.entryFrame.appendChild(n)
			self.entryFrame.sortChildren( self.getChildKey )

		if "cursor" in data.keys() and len( data["skellist"] ) == req.params[ "amount" ]:
			self._currentCursor[ req.reqType ] = data["cursor"]

			req.params[ "cursor" ] = data["cursor"]
			r = NetworkService.request(self.module,"list/%s" % req.reqType, req.params,
		                           successHandler=self.onRequestSucceded,
		                           failureHandler=self.showErrorMsg )
			r.reqType = req.reqType
			self._currentRequests.append( r )
		else:
			self._currentCursor[ req.reqType ] = None

		self.actionBar.resetLoadingState()

	def getChildKey(self, widget):
		"""
			Derives a string used to sort the entries in our entryframe
		"""
		name = (widget.data.get("name") or "").lower()

		if isinstance(widget, self.nodeWidget):
			return "0-%s" % name
		elif isinstance(widget, self.leafWidget):
			return "1-%s" % name
		else:
			return "2-"

	@staticmethod
	def canHandle(moduleName, moduleInfo):
		return moduleInfo["handler"].startswith("tree.")

	@staticmethod
	def render(moduleName, adminInfo, context):
		rootNode = context.get("rootNode") if context else None
		return TreeWidget(module=moduleName,rootNode=rootNode, context=context)

displayDelegateSelector.insert(1, TreeWidget.canHandle, TreeWidget)
moduleHandlerSelector.insert(1, TreeWidget.canHandle, TreeWidget.render)
