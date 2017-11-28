#-*- coding: utf-8 -*-

import html5, utils
from time import time
from network import NetworkService
from widgets.actionbar import ActionBar
from event import EventDispatcher
from priorityqueue import moduleHandlerSelector
from config import conf
from i18n import translate

class HierarchyItem( html5.Li ):
	"""
		Holds one entry in a hierarchy.
	"""
	def __init__(self, module, data, structure, *args, **kwargs):
		"""
			@param module: Name of the modul we shall display data for
			@type module: String
			@param data: The data for that entry
			@type data: Dict
			@param structure: Skeleton structure for that modul (as received  from the server)
			@type structure: List
		"""
		super( HierarchyItem, self ).__init__( *args, **kwargs )
		self.module = module
		self.data = data
		self.structure = structure
		self.expandLink = html5.A()
		self.expandLink["class"].append("expandlink")
		self.expandLink.appendChild(html5.TextNode(translate("Expand/Collapse")))
		self.appendChild(self.expandLink)
		#self.element.innerHTML = "%s %s" % (data["name"], data["sortindex"])
		self.isLoaded = False
		self.isExpanded = False
		self.buildDescription()
		self.ol = html5.Ol()
		self.ol["class"].append("subhierarchy")
		self.appendChild(self.ol)
		self.currentMargin = None
		self.ol["style"]["display"] = "none"
		self["class"].append("hierarchyitem")
		self["class"].append("unexpaned")
		self["class"].append("supports_drag")
		self["class"].append("supports_drop")
		self["draggable"] = True
		self.sinkEvent("onDragStart", "onDrop", "onDragOver","onDragLeave")

	def buildDescription(self):
		"""
			Generates the visual representation of this entry.
		"""
		format = "$(name)"

		if self.module in conf["modules"].keys():
			moduleInfo = conf["modules"][self.module]
			if "format" in moduleInfo.keys():
				format = moduleInfo["format"]

		self.appendChild(
				html5.TextNode(
						html5.utils.unescape(utils.formatString(format, self.data, self.structure,
						                                        language=conf["currentlanguage"]))))

	def onDragOver(self, event):
		"""
			Test wherever the current drag would mean "make it a child of us", "insert before us" or
			"insert after us" and apply the correct classes.
		"""
		height = self.element.offsetHeight
		offset = event.pageY - self.element.offsetTop

		# Before
		if self.currentMargin is None and offset < height * 0.20:
			self.currentMargin = "top"
			self["class"].remove("insert_here")
			self["class"].remove("insert_after")
			self["class"].append("insert_before")
		# After
		elif self.currentMargin is None and offset > height * 0.80:
			self.currentMargin = "bottom"
			self["class"].remove("insert_here")
			self["class"].remove("insert_before")
			self["class"].append("insert_after")
		# Within
		elif self.currentMargin and offset >= height * 0.20 and offset <= height * 0.80:
			self.currentMargin = None
			self["class"].remove("insert_before")
			self["class"].remove("insert_after")
			self["class"].append("insert_here")

		event.preventDefault()
		event.stopPropagation()

	def onDragLeave(self, event):
		"""
			Remove all drop indicating classes.
		"""
		self["class"].remove("insert_before")
		self["class"].remove("insert_after")
		self["class"].remove("insert_here")
		self.currentMargin = None
		super(HierarchyItem,self).onDragLeave( event )

	def onDragStart(self, event):
		"""
			We get dragged, store our id inside the datatransfer object.
		"""
		event.dataTransfer.setData( "Text", self.data["key"] )
		event.stopPropagation()

	def onDrop(self, event):
		"""
			We received a drop. Test wherever its means "make it a child of us", "insert before us" or
			"insert after us" and initiate the corresponding NetworkService requests.
		"""

		event.stopPropagation()
		event.preventDefault()

		height = self.element.offsetHeight
		offset = event.pageY - self.element.offsetTop

		srcKey = event.dataTransfer.getData("Text")

		if offset >= height * 0.20 and offset <= height * 0.80:
			print( "insert into" )
			# Just make the item a child of us
			NetworkService.request(self.module,"reparent",{"item":srcKey,"dest":self.data["key"]}, secure=True, modifies=True )
		elif offset < height * 0.20:
			#Insert this item *before* the current item
			print( "insert before" )
			parentID = self.data["parententry"]
			if parentID:
				lastIdx = 0
				for c in self.parent()._children:
					if "data" in dir(c) and "sortindex" in c.data.keys():
						if c == self:
							break
						lastIdx = c.data["sortindex"]
				newIdx = str((lastIdx+self.data["sortindex"])/2.0)
				req = NetworkService.request(self.module,"reparent",{"item":srcKey,"dest":parentID}, secure=True, successHandler=self.onItemReparented )
				req.newIdx = newIdx
				req.item = srcKey
		elif offset > height * 0.80:
			#Insert this item *after* the current item
			print( "insert after" )
			parentID = self.data["parententry"]

			if parentID:
				lastIdx = time()
				doUseNextChild = False
				for c in self.parent()._children:
					if "data" in dir(c) and "sortindex" in c.data.keys():
						if doUseNextChild:
							lastIdx = c.data["sortindex"]
							break
						if c == self:
							doUseNextChild = True

				newIdx = str((lastIdx+self.data["sortindex"])/2.0)
				req = NetworkService.request(self.module,"reparent",{"item":srcKey,"dest":parentID},
				                                secure=True, successHandler=self.onItemReparented )
				req.newIdx = newIdx
				req.item = srcKey

	def onItemReparented(self, req):
		"""
			Called after a reparent-request finished; run the setIndex request afterwards.
		"""
		assert "newIdx" in dir(req)
		NetworkService.request(self.module,"setIndex",{"item":req.item,"index":req.newIdx}, secure=True, modifies=True )

	def toggleExpand(self):
		"""
			Expands or unexpands this entry.
			If its expanded, its children (if any) become visible,
			otherwise the ol-tag (and all its children) are display: None
			Does *not* load its children when its first expanding - that has
			to be done by the HierarchyWidget.
		"""
		if self.isExpanded:
			self.ol["style"]["display"] = "none"
			self["class"].remove("expaned")
			self["class"].append("unexpaned")
		else:
			self.ol["style"]["display"] = "block"
			self["class"].append("expaned")
			self["class"].remove("unexpaned")

		self.isExpanded = not self.isExpanded

class HierarchyWidget(html5.Div):
	"""
		Displays a hierarchy where entries are direct children of each other.
		(There's only one type on entries in a HierarchyApplication. If you need to
		differentiate between nodes/leafs use a TreeApplication instead)
	"""

	def __init__(self, module, rootNode=None, isSelector=False, context=None, *args, **kwargs):
		"""
			@param module: Name of the modul we shall handle. Must be a hierarchy application!
			@type module: string
			@param rootNode: The repository we shall display. If none, we try to select one.
			@type rootNode: String or None
		"""
		super( HierarchyWidget, self ).__init__( )
		self.module = module
		self.rootNode = rootNode
		self.actionBar = ActionBar(module, "hierarchy")
		self.appendChild( self.actionBar )
		self.entryFrame = html5.Ol()
		self.entryFrame["class"].append("hierarchy")
		self.appendChild( self.entryFrame )
		self.selectionChangedEvent = EventDispatcher("selectionChanged")
		self.selectionActivatedEvent = EventDispatcher("selectionActivated")
		self.rootNodeChangedEvent = EventDispatcher("rootNodeChanged")
		self._currentCursor = None
		self._currentRequests = []
		self.addClass("supports_drop")
		self.isSelector = isSelector
		self._expandedNodes = []
		self.context = context

		if self.rootNode:
			self.reloadData()
		else:
			NetworkService.request(self.module, "listRootNodes",
			                       self.context or {},
			                       successHandler=self.onSetDefaultRootNode,
			                       failureHandler=self.showErrorMsg )

		self.path = []
		self.sinkEvent("onClick", "onDblClick")

		##Proxy some events and functions of the original table
		#for f in ["selectionChangedEvent","selectionActivatedEvent","cursorMovedEvent","getCurrentSelection"]:
		#	setattr( self, f, getattr(self.table,f))
		self.actionBar.setActions(["selectrootnode","add","edit","clone","delete"]+(["select","close"] if isSelector else [])+["reload"])
		self.sinkEvent("onDrop","onDragOver")


	def showErrorMsg(self, req=None, code=None):
		"""
			Removes all currently visible elements and displayes an error message
		"""
		self.actionBar["style"]["display"] = "none"
		self.entryFrame["style"]["display"] = "none"
		errorDiv = html5.Div()
		errorDiv["class"].append("error_msg")
		if code and (code==401 or code==403):
			txt = translate("Access denied!")
		else:
			txt = translate("An unknown error occurred!")
		errorDiv["class"].append("error_code_%s" % (code or 0))
		errorDiv.appendChild( html5.TextNode( txt ) )
		self.appendChild( errorDiv )

	def onDataChanged(self, module, **kwargs):

		if module != self.module:

			isRootNode = False
			for k, v in conf[ "modules" ].items():
				if (k == module
				    and v.get("handler") == "list"
				    and v.get("rootNodeOf") == self.module):

					isRootNode = True
					break

			if not isRootNode:
				return

		self.actionBar.widgets["selectrootnode"].update()
		self.reloadData()

	def onAttach(self):
		super( HierarchyWidget, self ).onAttach()
		NetworkService.registerChangeListener( self )

	def onDetach(self):
		super( HierarchyWidget, self ).onDetach()
		NetworkService.removeChangeListener( self )

	def itemForEvent(self,event, elem=None):
		"""
			Tries to map an event to one of our HierarchyItems.
			Returns the item actually clicked, not its top-level parent.
		"""
		if elem is None:
			elem = self.entryFrame
		for child in elem._children:
			if child.element==event.target:
				if isinstance( child, HierarchyItem ):
					# User clicked directly on one HierarchyItem
					return( child )
				else:
					# User clicked somewhere INTO one HierarchyItem
					# Return a marker to the outer recursion that this is the correct HierarchyItem
					return( False )
			tmp = self.itemForEvent( event, child )
			if tmp is False:
				if isinstance(child, HierarchyItem):
					return( child )
				else:
					return( False )
			elif tmp is not None:
				return( tmp )
		return( None )

	def itemForKey(self, key, elem=None ):
		"""
			Returns the HierarchyWidget displaying the entry with the given key.
			@param key: The key (id) of the item.
			@type key: string
			@returns: HierarchyItem
		"""
		if elem is None:
			elem = self.entryFrame
		for child in elem._children:
			if child.data["key"]==key:
				return( child )
			tmp = self.itemForKey( key, child.ol )
			if tmp is not None:
				return( tmp )
		return( None )

	def onClick(self, event):
		item = self.itemForEvent(event)

		if item is None:
			return

		if html5.utils.doesEventHitWidgetOrChildren(event, item.expandLink):
			item.toggleExpand()

			if not item.isLoaded:
				item.isLoaded = True
				self.loadNode(item.data["key"])

		else:
			self.setCurrentItem( item )
			self.selectionChangedEvent.fire( self, item )

	def onDblClick(self, event):
		item = self.itemForEvent( event )
		if item is None:
			return
		self.setCurrentItem( item )
		self.selectionActivatedEvent.fire( self, [item] )
		if self.isSelector:
			conf["mainWindow"].removeWidget(self)

	def setCurrentItem(self, item):
		if self._currentCursor:
			self._currentCursor["class"].remove("is_focused")
		item["class"].append("is_focused")
		self._currentCursor = item

	def onSetDefaultRootNode(self, req):
		"""
			We requested the list of rootNodes for that modul and that
			request just finished. Parse the respone and set our rootNode
			to the first rootNode received.
		"""
		data = NetworkService.decode( req )
		if len(data)>0:
			self.setRootNode( data[0]["key"])

	def setRootNode(self, rootNode):
		"""
			Set the currently displayed hierarchy to 'rootNode'.
			@param rootNode: Key of the rootNode which children we shall display
			@type rootNode: string
		"""
		self.rootNode = rootNode
		self._currentCursor = None
		self.rootNodeChangedEvent.fire(rootNode)
		self.reloadData()

	def reloadData(self):
		"""
			Reload the data were displaying.
		"""
		def collectExpandedNodes( currNode ):
			res = []
			for c in currNode._children[:]:
				if isinstance( c, HierarchyItem ):
					if c.isExpanded:
						res.append( c.data["key"] )
					res.extend( collectExpandedNodes(c.ol) )
			return( res )
		self._expandedNodes = collectExpandedNodes( self.entryFrame )
		self._currentRequests = []
		for c in self.entryFrame._children[:]:
			self.entryFrame.removeChild(c)
		self.loadNode( self.rootNode )

	def loadNode(self, node, cursor = None):
		"""
			Fetch the (direct) children of the given node.
			Once the list is received, append them to their parent node.
			@param node: Key of the node to fetch
			@type node: string
		"""
		params = {
			"parent": node,
		    "orderby": "sortindex"
		}

		if cursor:
			params.update({"cursor": cursor})

		if self.context:
			params.update(self.context)

		r = NetworkService.request(self.module, "list",
		                            params,
		                            successHandler=self.onRequestSucceded,
		                            failureHandler=self.showErrorMsg)
		r.node = node
		self._currentRequests.append(r)

	def onRequestSucceded(self, req):
		"""
			The NetworkRequest for a (sub)node finished.
			Create a new HierarchyItem for each entry received and add them to our view
		"""
		if not req in self._currentRequests:
			#Prevent inserting old (stale) data
			self.actionBar.resetLoadingState()
			return

		self._currentRequests.remove(req)
		data = NetworkService.decode(req)

		if req.node == self.rootNode:
			ol = self.entryFrame
		else:
			tmp = self.itemForKey(req.node)
			ol = tmp.ol
			assert ol is not None

		for skel in data["skellist"]:
			hi = HierarchyItem( self.module, skel, data["structure"] )
			ol.appendChild( hi )
			if hi.data["key"] in self._expandedNodes:
				hi.toggleExpand()
				if not hi.isLoaded:
					hi.isLoaded = True
					self.loadNode(hi.data["key"])

		if not ol._children and ol != self.entryFrame:
			ol.parent()["class"].append("has_no_childs")

		if data["skellist"] and data["cursor"]:
			self.loadNode(req.node, data["cursor"])

		self.actionBar.resetLoadingState()

	def getCurrentSelection(self):
		"""
			Returns the list of entries currently selected.
			@returns: list of dict
		"""
		if self._currentCursor is not None:
			return( [ self._currentCursor.data ] )
		return( [] )

	def onDrop(self, event):
		"""
			We got a drop event. Make that item a direct child of our rootNode
		"""
		srcKey = event.dataTransfer.getData("Text")
		NetworkService.request(self.module,"reparent",{"item":srcKey,"dest":self.rootNode}, secure=True, modifies=True )
		event.stopPropagation()

	def onDragOver(self, event):
		"""
			Allow dropping children on the rootNode
		"""
		event.preventDefault()
		event.stopPropagation()

	def activateCurrentSelection(self):
		if self._currentCursor:
			self.selectionActivatedEvent.fire( self, [self._currentCursor] )
			conf["mainWindow"].removeWidget(self)

	@staticmethod
	def canHandle(moduleName, moduleInfo):
		return moduleInfo["handler"] == "hierarchy" or moduleInfo["handler"].startswith("hierarchy.")

	@staticmethod
	def render(moduleName, adminInfo, context):
		if "@rootNode" in context:
			rootNode = context["@rootNode"]
			del context["@rootNode"]
		else:
			rootNode = None

		return HierarchyWidget(module=moduleName, rootNode=rootNode, context=context)

moduleHandlerSelector.insert(1, HierarchyWidget.canHandle, HierarchyWidget.render)
