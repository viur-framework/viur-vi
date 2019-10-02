#-*- coding: utf-8 -*-
from vi import html5
import vi.utils as utils

from vi.network import NetworkService
from vi.widgets.actionbar import ActionBar
from vi.event import EventDispatcher
from vi.priorityqueue import moduleHandlerSelector, viewDelegateSelector
from vi.config import conf
from vi.i18n import translate
from vi.embedsvg import embedsvg
from vi.widgets.list import ListWidget

from time import time


class HierarchyItem(html5.Li):
	"""
		Holds one entry in a hierarchy.
	"""
	def __init__(self, module, data, structure,widget, *args, **kwargs):
		"""
			:param module: Name of the module we shall display data for
			:type module: str
			:param data: The data for that entry
			:type data: dict
			:param structure: Skeleton structure for that module (as received  from the server)
			:type structure: list
			:param widget: parent Widget
			:type structure: HierarchyWidget
		"""
		super( HierarchyItem, self ).__init__( *args, **kwargs )
		self.module = module
		self.data = data
		self.structure = structure
		self.widget = widget
		self.expandLink = html5.A()
		self.expandLink.addClass("expandlink")
		self.expandLink.addClass("hierarchy-toggle")
		self.expandLink["title"] = translate("Expand/Collapse")
		embedSvg = embedsvg.get("icons-arrow-right")
		if embedSvg:
			self.expandLink.element.innerHTML = embedSvg + self.expandLink.element.innerHTML
		self.prependChild(self.expandLink)

		#self.element.innerHTML = "%s %s" % (data["name"], data["sortindex"])
		self.isLoaded = False
		self.isExpanded = False
		self.buildDescription()
		self.ol = html5.Ol()
		self.ol.addClass("hierarchy-sublist")
		self.appendChild(self.ol)
		self.currentMargin = None
		self.ol["style"]["display"] = "none"

		self.addClass("hierarchy-item")
		self.addClass("is-collapsed")
		self.addClass("is-draggable")
		self.addClass("is-drop-target")
		self["draggable"] = True
		self.sinkEvent("onDragStart", "onDrop", "onDragOver","onDragLeave")

		self.afterDiv = html5.Div()
		self.afterDiv["class"] = ["after-element"]
		self.afterDiv.hide()
		aftertxt = html5.TextNode(translate(u"Nach dem Element einfügen"))
		self.afterDiv.appendChild(aftertxt)
		self.appendChild( self.afterDiv )

		self.beforeDiv = html5.Div()
		self.beforeDiv[ "class" ] = [ "before-element" ]
		self.beforeDiv.hide()
		beforetxt = html5.TextNode( translate( u"Vor dem Element einfügen" ) )
		self.beforeDiv.appendChild( beforetxt )
		self.prependChild(self.beforeDiv)

		self.currentStatus = None


	def buildDescription(self):
		"""
			Creates the visual representation of our entry
		"""
		# Find any bones in the structure having "frontend_default_visible" set.
		hasDescr = False

		for boneName, boneInfo in self.structure:
			if "params" in boneInfo.keys() and isinstance(boneInfo["params"], dict):
				params = boneInfo["params"]
				if "frontend_default_visible" in params and params["frontend_default_visible"]:
					structure = {k: v for k, v in self.structure}
					wdg = viewDelegateSelector.select(self.module, boneName, structure)

					if wdg is not None:
						self.appendChild(wdg(self.module, boneName, structure).render(self.data, boneName))
						hasDescr = True

		# In case there is no bone configured for visualization, use a format-string
		if not hasDescr:
			format = "$(name)" #default fallback

			if self.module in conf["modules"].keys():
				moduleInfo = conf["modules"][self.module]
				if "format" in moduleInfo.keys():
					format = moduleInfo["format"]

			self.appendChild(html5.utils.unescape(
				utils.formatString(format, self.data, self.structure,
				    language=conf["currentlanguage"])))

	def onDragOver(self, event):
		"""
			Test wherever the current drag would mean "make it a child of us", "insert before us" or
			"insert after us" and apply the correct classes.
		"""
		self.afterDiv.show() #show dropzones
		self.beforeDiv.show()

		self.leaveElement = False #reset leaveMarker

		self[ "title" ] = translate( "vi.data-insert" )
		if event.target == self.beforeDiv.element:
			self.currentStatus = "top"
			self.removeClass( "insert-here" )
			self.beforeDiv.addClass("is-focused")
			self.afterDiv.removeClass( "is-focused" )
		elif event.target == self.afterDiv.element:
			self.currentStatus = "bottom"
			self.removeClass( "insert-here" )
			self.beforeDiv.removeClass("is-focused")
			self.afterDiv.addClass( "is-focused" )

		elif event.target == self.element:
			self.currentStatus = "inner"
			self.addClass( "insert-here" )
			self.beforeDiv.removeClass( "is-focused" )
			self.afterDiv.removeClass( "is-focused" )
			self[ "title" ] = translate( u"In das Element einfügen" )


		event.preventDefault()
		event.stopPropagation()



	def disableDragMarkers( self ):
		if self.leaveElement:
			self[ "title" ] = translate( "vi.data-insert" )
			self.currentStatus = None
			self.afterDiv.hide()
			self.beforeDiv.hide()
			self.removeClass( "insert-here" )
		else:
			self.leaveElement = True
			w = eval( "window" )
			w.setTimeout( self.disableDragMarkers, 2000 )

	def onDragLeave(self, event):
		"""
			Remove all drop indicating classes.
		"""

		# Only leave if target not before or after
		if event.target == self.beforeDiv.element:
			self.leaveElement =False
			return
		elif event.target == self.afterDiv.element:
			self.leaveElement = False
			return
		else:
			self.leaveElement = True

		w = eval("window")
		w.setTimeout(self.disableDragMarkers,1) #test later to leave, to avoid flickering...

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
		srcKey = event.dataTransfer.getData( "Text" )

		if self.currentStatus == "inner":
			NetworkService.request( self.module, "reparent",
			                        { "item":srcKey, "dest":self.data[ "key" ] },
			                        secure = True, modifies = True )
		elif self.currentStatus == "top":
			parentID = self.data[ "parententry" ]
			if parentID:
				lastIdx = 0
				for c in self.parent()._children:
					if "data" in dir( c ) and "sortindex" in c.data.keys():
						if c == self:
							break
						lastIdx = c.data[ "sortindex" ]
				newIdx = str( (lastIdx + self.data[ "sortindex" ]) / 2.0 )
				req = NetworkService.request( self.module, "reparent", { "item":srcKey, "dest":parentID },
				                              secure = True, successHandler = self.onItemReparented )
				req.newIdx = newIdx
				req.item = srcKey



		elif self.currentStatus == "bottom":
			parentID = self.data[ "parententry" ]

			if parentID:
				lastIdx = time()
				doUseNextChild = False
				for c in self.parent()._children:
					if "data" in dir( c ) and "sortindex" in c.data.keys():
						if doUseNextChild:
							lastIdx = c.data[ "sortindex" ]
							break
						if c == self:
							doUseNextChild = True

				newIdx = str( (lastIdx + self.data[ "sortindex" ]) / 2.0 )
				req = NetworkService.request( self.module, "reparent", { "item":srcKey, "dest":parentID },
				                              secure = True, successHandler = self.onItemReparented )
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
			self.removeClass("is-expanded")
			self.addClass("is-collapsed")
		else:
			self.ol["style"]["display"] = "block"
			self.addClass("is-expanded")
			self.removeClass("is-collapsed")

		self.isExpanded = not self.isExpanded

class HierarchyWidget(html5.Div):
	"""
		Displays a hierarchy where entries are direct children of each other.
		(There's only one type on entries in a HierarchyApplication. If you need to
		differentiate between nodes/leafs use a TreeApplication instead)
	"""

	def __init__(self, module, rootNode=None, selectMode=None, context=None, *args, **kwargs):
		"""
			:param module: Name of the module we shall handle. Must be a hierarchy application!
			:type module: str
			:param rootNode: The repository we shall display. If none, we try to select one.
			:type rootNode: str or None
		"""
		super( HierarchyWidget, self ).__init__( )
		self.module = module
		self.rootNode = rootNode
		self.addClass("vi-widget vi-widget--hierarchy")
		self.actionBar = ActionBar(module, "hierarchy")
		self.appendChild( self.actionBar )

		self.entryFrame = html5.Ol()
		self.entryFrame.addClass("hierarchy")
		self.appendChild( self.entryFrame )
		self.selectionChangedEvent = EventDispatcher("selectionChanged")
		self.selectionActivatedEvent = EventDispatcher("selectionActivated")
		self.rootNodeChangedEvent = EventDispatcher("rootNodeChanged")
		self._currentCursor = None
		self._currentRequests = []
		self.addClass("is-drop-target")

		assert selectMode in [None, "single", "multi"]
		self.selectMode = selectMode

		self._expandedNodes = []
		self.context = context

		#listview
		self.currentKey = None
		self.listview = ListWidget( self.module, context = self.context, autoload = False )
		self.listview.actionBar.setActions(["preview", "selectfields"] )
		self.listwidgetadded = False
		self.listviewActiv = False
		self.setListView( self.listviewActiv )


		if self.rootNode:
			self.reloadData()
		else:
			NetworkService.request(self.module, "listRootNodes",
			                       self.context or {},
			                       successHandler=self.onSetDefaultRootNode,
			                       failureHandler=self.showErrorMsg )

		self.path = []
		self.sinkEvent("onClick", "onDblClick")

		self.actionBar.setActions(["selectrootnode","add","edit","clone","delete"]+(["select","close"] if self.selectMode else [])+["|","listview","reload"])
		self.sinkEvent("onDrop","onDragOver")

	def toggleListView( self ):
		self.setListView(not self.listviewActive)
		self.reloadData()

	def setListView( self,visible=False ):
		if visible:
			self[ "style" ][ "width" ] = "33%"
			self.listviewActive = True
			self.showListView()
			return
		self.listviewActive = False
		self.hideListView()
		self["style"]["width"]="100%"

	def showListView( self ):
		self.listview.show()

	def hideListView( self ):
		self.listview.hide()

	def showErrorMsg(self, req=None, code=None):
		"""
			Removes all currently visible elements and displayes an error message
		"""
		self.actionBar["style"]["display"] = "none"
		self.entryFrame["style"]["display"] = "none"
		errorDiv = html5.Div()
		errorDiv.addClass("popup popup--center popup--local msg msg--error is-active error_msg")
		if code and (code==401 or code==403):
			txt = translate("Access denied!")
		else:
			txt = translate("An unknown error occurred!")
		errorDiv.addClass("error_code_%s" % (code or 0))
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
			:param key: The key (id) of the item.
			:type key: str
			:returns: HierarchyItem
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
		if event.target == self.element:
			#empty click
			self.currentKey = self.rootNode
			self.setCurrentItem(None)
			if self.listviewActive:
				self.reloadListWidget()

		item = self.itemForEvent(event)

		if item is None:
			return

		currentKey = item.data["key"]
		self.currentKey = currentKey

		if html5.utils.doesEventHitWidgetOrChildren(event, item.expandLink):
			item.toggleExpand()

			if not item.isLoaded:
				item.isLoaded = True
				self.loadNode(self.currentKey)

		else:
			self.setCurrentItem( item )
			self.selectionChangedEvent.fire( self, item )

		if self.listviewActive:
			self.reloadListWidget()



	def onDblClick(self, event):
		item = self.itemForEvent( event )
		if item is None:
			return
		self.setCurrentItem( item )
		self.selectionActivatedEvent.fire( self, [item] )
		if self.selectMode:
			conf["mainWindow"].removeWidget(self)

	def setCurrentItem(self, item):
		if self._currentCursor:
			self._currentCursor.removeClass("is-focused")

		if item:
			item.addClass("is-focused")
			self._currentCursor = item

	def onSetDefaultRootNode(self, req):
		"""
			We requested the list of rootNodes for that module and that
			request just finished. Parse the respone and set our rootNode
			to the first rootNode received.
		"""
		data = NetworkService.decode( req )
		if len(data)>0:
			self.setRootNode( data[0]["key"])

	def setRootNode(self, rootNode):
		"""
			Set the currently displayed hierarchy to 'rootNode'.
			:param rootNode: Key of the rootNode which children we shall display
			:type rootNode: str
		"""
		self.rootNode = rootNode
		self.currentKey = self.rootNode
		self._currentCursor = None
		self.rootNodeChangedEvent.fire(rootNode)
		self.reloadData()

	def reloadData(self):
		"""
			Reload the data were displaying.
		"""
		if self.listviewActive and not self.listwidgetadded:
			self.listwidgetadded= True
			conf[ "mainWindow" ].stackWidget( self.listview,disableOtherWidgets=False )

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
		if self.listviewActive:
			self.reloadListWidget()


	def reloadListWidget( self ):
		self.listview.setFilter( { "parent":self.currentKey,"orderby":"sortindex" } )

	def loadNode(self, node, cursor = None):
		"""
			Fetch the (direct) children of the given node.
			Once the list is received, append them to their parent node.
			:param node: Key of the node to fetch
			:type node: str
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
			hi = HierarchyItem( self.module, skel, data["structure"],self )
			ol.appendChild( hi )
			if hi.data["key"] in self._expandedNodes:
				hi.toggleExpand()
				if not hi.isLoaded:
					hi.isLoaded = True
					self.loadNode(hi.data["key"])

		if not ol._children and ol != self.entryFrame:
			ol.parent().addClass("has-no-child")

		if data["skellist"] and data["cursor"]:
			self.loadNode(req.node, data["cursor"])

		self.actionBar.resetLoadingState()

	def getCurrentSelection(self):
		"""
			Returns the list of entries currently selected.
			:returns: list of dict
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
		rootNode = context.get(conf["vi.context.prefix"] + "rootNode") if context else None
		return HierarchyWidget(module=moduleName, rootNode=rootNode, context=context)

moduleHandlerSelector.insert(1, HierarchyWidget.canHandle, HierarchyWidget.render)
