# -*- coding: utf-8 -*-
from vi import html5, utils
from vi.network import NetworkService
from vi.framework.components.actionbar import ActionBar
from vi.framework.event import EventDispatcher
from vi.priorityqueue import displayDelegateSelector, boneSelector, moduleWidgetSelector
from vi.config import conf
from vi.i18n import translate
from vi.embedsvg import embedsvg
from time import time


class TreeItemWidget(html5.Li):
	def __init__(self, module, data, structure, widget, *args, **kwargs):
		"""
			:param module: Name of the module for which we'll display data
			:type module: str
			:param data: The data we're going to display
			:type data: dict
			:param structure: The structure of that data as received from server
			:type structure: list
			:param widget: tree widget
		"""
		super(TreeItemWidget, self).__init__()
		self["class"] = "vi-tree-item item has-hover is-drop-target is-draggable"
		self.module = module
		self.data = data

		self.currentStatus = None

		self.structure = structure
		self.widget = widget

		self.isExpanded = False
		self.childrenLoaded = False
		self.isDragged = False

		self.sortindex = data["sortindex"] if "sortindex" in data else 0

		self.fromHTML("""
			<div style="flex-direction:column;width:100%" [name]="nodeWrapper">
				<div class="item" [name]="nodeGrouper">
					<a class="expandlink hierarchy-toggle" [name]="nodeToggle"></a>
					<div class="item-image is-hidden" [name]="nodeImage"></div>
					<div class="item-content" [name]="nodeContent">
						<div class="item-headline" [name]="nodeHeadline"></div>
						<div class="item-subline" [name]="nodeSubline"></div>
					</div>
					<div class="item-controls" [name]="nodeControls"></div>
				</div>

				<ol class="hierarchy-sublist is-hidden" [name]="ol"></ol>
			</div>
		""")

		self["draggable"] = True

		self.sinkEvent("onDragOver", "onDrop", "onDragStart", "onDragLeave", "onDragEnd")

		self.setStyle()

		self.sinkEvent("onClick", "onDragStart")

	def setStyle(self):
		'''
			is used to define the appearance of the element
		'''
		self["class"].append("hierarchy-item")
		self.additionalDropAreas()
		self.buildDescription()
		self.toggleArrow()

	# self.EntryIcon()

	def additionalDropAreas(self):
		'''
			Drag and Drop areas
		'''
		self.afterDiv = html5.Div()
		self.afterDiv["class"] = ["after-element"]
		self.afterDiv.hide()
		aftertxt = html5.TextNode(translate(u"Nach dem Element einfügen"))
		self.afterDiv.appendChild(aftertxt)
		self.nodeWrapper.appendChild(self.afterDiv)

		self.beforeDiv = html5.Div()
		self.beforeDiv["class"] = ["before-element"]
		self.beforeDiv.hide()
		beforetxt = html5.TextNode(translate(u"Vor dem Element einfügen"))
		self.beforeDiv.appendChild(beforetxt)
		self.nodeWrapper.prependChild(self.beforeDiv)

	def markDraggedElement(self):
		'''
			mark the current dragged Element
		'''
		self["style"]["opacity"] = "0.5"

	def unmarkDraggedElement(self):
		self["style"]["opacity"] = "1"

	def onDragStart(self, event):
		event.dataTransfer.setData("Text", "%s/%s" % (self.data["key"], self.skelType))
		self.isDragged = True
		self.markDraggedElement()
		event.stopPropagation()

	def onDragEnd(self, event):
		self.isDragged = False
		self.unmarkDraggedElement()

		if "afterDiv" in dir(self) or "beforeDiv" in dir(self):
			self.disableDragMarkers()

	def onDragOver(self, event):
		"""
			Test wherever the current drag would mean "make it a child of us", "insert before us" or
			"insert after us" and apply the correct classes.
		"""
		if self.isDragged:
			return

		if "afterDiv" in dir(self):
			self.afterDiv.show()  # show dropzones
		if "beforeDiv" in dir(self):
			self.beforeDiv.show()

		self.leaveElement = False  # reset leaveMarker

		self["title"] = translate("vi.data-insert")
		if "beforeDiv" in dir(self) and event.target == self.beforeDiv.element:
			self.currentStatus = "top"
			self.removeClass("insert-here")
			self.beforeDiv.addClass("is-focused")
			self.afterDiv.removeClass("is-focused")

		elif "afterDiv" in dir(self) and event.target == self.afterDiv.element:
			self.currentStatus = "bottom"
			self.removeClass("insert-here")
			self.beforeDiv.removeClass("is-focused")
			self.afterDiv.addClass("is-focused")

		elif html5.utils.doesEventHitWidgetOrChildren(event, self):
			self.currentStatus = "inner"
			self.addClass("insert-here")
			if "beforeDiv" in dir(self):
				self.beforeDiv.removeClass("is-focused")
			if "afterDiv" in dir(self):
				self.afterDiv.removeClass("is-focused")
			self["title"] = translate(u"In das Element einfügen")

		event.preventDefault()
		event.stopPropagation()

	def onDragLeave(self, event):
		"""
			Remove all drop indicating classes.
		"""
		# Only leave if target not before or after
		if html5.utils.doesEventHitWidgetOrChildren(event, self.nodeWrapper):
			self.leaveElement = False
			return
		else:
			self.leaveElement = True

		if "beforeDiv" in dir(self) or "afterDiv" in dir(self):
			w = html5.window
			w.setTimeout(self.disableDragMarkers, 2000)  # test later to leave, to avoid flickering...

	def disableDragMarkers(self):
		if self.leaveElement:
			self["title"] = translate("vi.data-insert")
			self.currentStatus = None
			if self.afterDiv:
				self.afterDiv.hide()
			if self.beforeDiv:
				self.beforeDiv.hide()
			self.removeClass("insert-here")
		else:
			self.leaveElement = True
			w = html5.window
			w.setTimeout(self.disableDragMarkers, 5000)

	def onDrop(self, event):
		"""
			We received a drop. Test wherever its means "make it a child of us", "insert before us" or
			"insert after us" and initiate the corresponding NetworkService requests.
		"""
		event.stopPropagation()
		event.preventDefault()
		srcKey, skelType = event.dataTransfer.getData("Text").split("/")

		if self.currentStatus == "inner":
			NetworkService.request(self.module, "move",
			                       {"skelType": skelType, "key": srcKey, "parentNode": self.data["key"]},
			                       secure=True, modifies=True)

		elif self.currentStatus == "top":
			parentID = self.data["parententry"]
			if parentID:
				lastIdx = 0
				for c in self.parent()._children:
					if "data" in dir(c) and "sortindex" in c.data.keys():
						if c == self:
							break
						lastIdx = float(c.data["sortindex"])
				newIdx = str((lastIdx + float(self.data["sortindex"])) / 2.0)
				req = NetworkService.request(self.module, "move",
				                             {"skelType": skelType, "key": srcKey, "parentNode": parentID,
				                              "sortindex": newIdx},
				                             secure=True, modifies=True)



		elif self.currentStatus == "bottom":
			parentID = self.data["parententry"]

			if parentID:
				lastIdx = time()
				doUseNextChild = False
				for c in self.parent()._children:
					if "data" in dir(c) and "sortindex" in c.data.keys():
						if doUseNextChild:
							lastIdx = float(c.data["sortindex"])
							break
						if c == self:
							doUseNextChild = True

				newIdx = str((lastIdx + float(self.data["sortindex"])) / 2.0)
				req = NetworkService.request(self.module, "move",
				                             {"skelType": skelType, "key": srcKey, "parentNode": parentID,
				                              "sortindex": newIdx},
				                             secure=True, modifies=True)

	def EntryIcon(self):
		self.nodeImage.removeClass("is-hidden")
		svg = embedsvg.get("icons-folder")
		if svg:
			nodeIcon = html5.I()
			nodeIcon.addClass("i")
			nodeIcon.element.innerHTML = svg + nodeIcon.element.innerHTML
			self.nodeImage.appendChild(nodeIcon)

	def toggleArrow(self):
		self.nodeToggle["title"] = translate("Expand/Collapse")
		embedSvg = embedsvg.get("icons-arrow-right")
		if embedSvg:
			self.nodeToggle.element.innerHTML = embedSvg + self.nodeToggle.element.innerHTML

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
					wdg = boneSelector.select(self.module, boneName, structure)

					if wdg is not None:
						self.nodeHeadline.appendChild(
							wdg(self.module, boneName, structure).viewWidget(self.data[boneName])
						)
						hasDescr = True

		# In case there is no bone configured for visualization, use a format-string
		if not hasDescr:
			format = "$(name)"  # default fallback

			if self.module in conf["modules"].keys():
				moduleInfo = conf["modules"][self.module]
				if "format" in moduleInfo.keys():
					format = moduleInfo["format"]

			self.nodeHeadline.appendChild(
				utils.formatString(format, self.data, self.structure,
				                   language=conf["currentLanguage"]))

			if self.data and "size" in self.data and self.data["size"]:
				def convert_bytes(num):
					step_unit = 1000.0  # 1024 size

					for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
						if num < step_unit:
							return "%3.1f %s" % (num, x)
						num /= step_unit

				size = convert_bytes(int(self.data["size"]))
				self.nodeSubline.appendChild(html5.TextNode(size))

	def onClick(self, event):
		if event.target != self.nodeToggle.element:
			self.widget.extendSelection(self)

		else:
			self.toggleExpand()

		event.preventDefault()
		event.stopPropagation()

	def toggleExpand(self):
		'''
			Toggle a Node and request if needed child elements
		'''

		if self.isExpanded:
			self.ol.addClass("is-hidden")
			self.nodeGrouper.removeClass("is-expanded")
			self.nodeGrouper.addClass("is-collapsed")
			self.removeClass("is-expanded")
			self.addClass("is-collapsed")
		else:
			self.ol.removeClass("is-hidden")
			self.nodeGrouper.addClass("is-expanded")
			self.nodeGrouper.removeClass("is-collapsed")
			self.addClass("is-expanded")
			self.removeClass("is-collapsed")

		self.isExpanded = not self.isExpanded

		if not self.childrenLoaded:
			self.childrenLoaded = True
			self.widget.requestChildren(self)


class TreeLeafWidget(TreeItemWidget):
	skelType = "leaf"

	def setStyle(self):
		'''
			Leaf have a different color
		'''
		super(TreeLeafWidget, self).setStyle()
		self["style"]["background-color"] = "#f7edd2"

	def toggleArrow(self):
		'''
			Leafes cant be toggled
		'''
		if self.skelType == "leaf":
			self.nodeToggle["style"]["width"] = "27px"

	def EntryIcon(self):
		'''
			Leafs have a different Icon
		'''
		self.nodeImage.removeClass("is-hidden")
		svg = embedsvg.get("icons-file")
		if svg:
			nodeIcon = html5.I()
			nodeIcon.addClass("i")
			nodeIcon.element.innerHTML = svg + nodeIcon.element.innerHTML
			self.nodeImage.appendChild(nodeIcon)


class TreeNodeWidget(TreeItemWidget):
	skelType = "node"


class TreeWidget(html5.Div):
	"""
			Displays a hierarchy where entries are direct children of each other.
			(There's only one type on entries in a HierarchyApplication. If you need to
			differentiate between nodes/leafs use a TreeApplication instead)
		"""

	nodeWidget = TreeNodeWidget
	leafWidget = TreeLeafWidget

	def __init__(self, module, rootNode=None, node=None, context=None, *args, **kwargs):
		"""
			:param module: Name of the module we shall handle. Must be a hierarchy application!
			:type module: str
			:param rootNode: The repository we shall display. If none, we try to select one.
			:type rootNode: str or None
		"""
		super(TreeWidget, self).__init__()

		self.module = module
		self.rootNode = rootNode
		self.node = node or rootNode
		self.addClass("vi-widget vi-widget--hierarchy")
		self.actionBar = ActionBar(module, "tree")
		self.appendChild(self.actionBar)

		self.breadcrumb()

		self._isCtlPressed = False

		self.entryFrame = html5.Ol()
		self.entryFrame.addClass("hierarchy")
		self.appendChild(self.entryFrame)
		self.selectionChangedEvent = EventDispatcher("selectionChanged")
		self.selectionActivatedEvent = EventDispatcher("selectionActivated")
		self.rootNodeChangedEvent = EventDispatcher("rootNodeChanged")
		self.nodeChangedEvent = EventDispatcher("nodeChanged")

		self.allowMultiSelection = True
		self.currentSelectedElements = []

		self._currentCursor = None
		self._currentRequests = []
		self.addClass("is-drop-target")

		self.selectMulti = True
		self.selectCallback = None

		self._expandedNodes = []
		self.context = context

		if self.rootNode:
			self.reloadData()
		else:
			NetworkService.request(
				self.module,
				"listRootNodes",
				self.context or {},
				successHandler=self.onSetDefaultRootNode,
				failureHandler=self.showErrorMsg
			)

		self.path = []
		self.sinkEvent("onKeyDown", "onKeyUp", "onClick", "onDblClick", "onDrop", "onDragOver", "onDragLeave",
		               "onDragEnd")
		self.setSelector(None)
		self.selectionChangedEvent.register(self)
		self.buildSideWidget()

	def selectGuard(self, child):
		"""
		Guard function, checking if child does match a "selectable" item of this widget.
		"""
		print("selectGuard", child)
		return isinstance(child, (TreeNodeWidget, TreeLeafWidget))

	def buildSideWidget(self):
		'''
			Currently used by hierarchy widget
		'''
		return 0

	def breadcrumb(self):
		'''
			Currently used by treebrowser and file widget
		'''
		return 0

	def rebuildPath(self):
		'''
			Currently used by treebrowser and file widget
		'''
		return 0

	def clearSelection(self):
		for e in self.currentSelectedElements:
			e.removeClass("is-focused")

		self.currentSelectedElements = []

	def extendSelection(self, element):
		"""
		Extends the current selection to element.
		"""

		print("extendSelection", element.data)
		if self.selectGuard and not self.selectGuard(element):
			print("Oh ich bin nicht im guard")
			return False

		# Perform selection
		if self._isCtlPressed and self.selectMulti:
			if element in self.currentSelectedElements:
				self.currentSelectedElements.remove(element)
				element.removeClass("is-focused")
			else:
				self.currentSelectedElements.append(element)
				element.addClass("is-focused")
		else:
			self.clearSelection()

			if element:
				element.addClass("is-focused")
				self.currentSelectedElements = [element]
			else:
				self.currentSelectedElements = []

		self.selectionChangedEvent.fire(self, self.currentSelectedElements)
		return bool(self.currentSelectedElements)

	def requestChildren(self, element):
		self.loadNode(element.data["key"])

	def setSelector(self, callback):
		"""
		Configures the widget as a selector.
		"""
		self.selectCallback = callback
		self.actionBar.setActions(
			(["select", "close", "|"] if self.selectCallback else [])
			+ [
				"selectrootnode",
				"add",
				"add.node",
				"add.leaf",
				"edit",
				"clone",
				"delete",
				"|",
				"listview",
				"reload"
			],
			widget=self
		)

	def showErrorMsg(self, req=None, code=None):
		"""
			Removes all currently visible elements and displayes an error message
		"""

		self.actionBar["style"]["display"] = "none"
		self.entryFrame["style"]["display"] = "none"
		errorDiv = html5.Div()
		errorDiv.addClass("popup popup--center popup--local msg msg--error is-active error_msg")
		if code and (code == 401 or code == 403):
			txt = translate("Access denied!")
		else:
			txt = translate("An unknown error occurred!")
		errorDiv.addClass("error_code_%s" % (code or 0))
		errorDiv.appendChild(html5.TextNode(txt))
		self.appendChild(errorDiv)

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

		self.actionBar.widgets["selectrootnode"].update()
		self.reloadData()

	def onAttach(self):
		super(TreeWidget, self).onAttach()
		NetworkService.registerChangeListener(self)

	def onDetach(self):
		super(TreeWidget, self).onDetach()
		NetworkService.removeChangeListener(self)

	def itemForKey(self, key, elem=None):
		"""
			Returns the HierarchyWidget displaying the entry with the given key.
			:param key: The key (id) of the item.
			:type key: str
			:returns: HierarchyItem
		"""
		if elem is None:
			elem = self.entryFrame
		for child in elem._children:
			if child.data["key"] == key:
				return (child)
			tmp = self.itemForKey(key, child.ol)
			if tmp is not None:
				return (tmp)
		return (None)

	def onClick(self, event):
		if event.target == self.element:
			# empty click
			self.clearSelection()
			self.selectionChangedEvent.fire(self, self.currentSelectedElements)

	def onDblClick(self, event):
		for child in self.entryFrame.children():
			if html5.utils.doesEventHitWidgetOrChildren(event, child):
				print("OnDblClick")

				if self.selectCallback:
					print("selectMode")
					self.clearSelection()
					if self.extendSelection(child):
						self.activateCurrentSelection()
				elif isinstance(child, TreeNodeWidget):
					print("ToggleMode")
					child.toggleExpand()

				break

	def onSetDefaultRootNode(self, req):
		"""
			We requested the list of rootNodes for that module and that
			request just finished. Parse the respone and set our rootNode
			to the first rootNode received.
		"""
		data = NetworkService.decode(req)
		if len(data) > 0:
			self.setRootNode(data[0]["key"], self.node)

	def setRootNode(self, rootNode, node=None):
		"""
			Set the currently displayed hierarchy to 'rootNode'.
			:param rootNode: Key of the rootNode which children we shall display
			:type rootNode: str
		"""
		self.rootNode = rootNode
		self.node = node or rootNode
		self.currentKey = self.rootNode
		self._currentCursor = None
		self.rootNodeChangedEvent.fire(rootNode)
		if node:
			self.nodeChangedEvent.fire(node)
		self.reloadData()

	def reloadData(self):
		"""
			Reload the data were displaying.
		"""

		def collectExpandedNodes(currNode):
			res = []
			for c in currNode._children[:]:
				if isinstance(c, TreeItemWidget):
					if c.isExpanded:
						res.append(c.data["key"])
					res.extend(collectExpandedNodes(c.ol))
			return (res)

		self._expandedNodes = collectExpandedNodes(self.entryFrame)
		self._currentRequests = []
		for c in self.entryFrame._children[:]:
			self.entryFrame.removeChild(c)
		self.loadNode(self.rootNode)
		self.rebuildPath()

	def loadNode(self, node, cursor=None, overrideParams=None):
		"""
			Fetch the (direct) children of the given node.
			Once the list is received, append them to their parent node.
			:param node: Key of the node to fetch
			:type node: str
		"""
		self.node = node

		params = {
			"parententry": node,
			"orderby": "sortindex",
			"amount": 99
		}

		if cursor:
			params.update({"cursor": cursor})

		if overrideParams:
			params.update(overrideParams)

		if self.context:
			params.update(self.context)

		r = NetworkService.request(self.module, "list/node",
		                           params,
		                           successHandler=self.onRequestSucceded,
		                           failureHandler=self.showErrorMsg)
		r.reqType = "node"
		r.node = node
		self._currentRequests.append(r)

		if self.leafWidget:
			r = NetworkService.request(self.module, "list/leaf", params,
			                           successHandler=self.onRequestSucceded,
			                           failureHandler=self.showErrorMsg)
			r.reqType = "leaf"
			r.node = node
			self._currentRequests.append(r)

	def onRequestSucceded(self, req):
		"""
			The NetworkRequest for a (sub)node finished.
			Create a new HierarchyItem for each entry received and add them to our view
		"""
		if not req in self._currentRequests:
			# Prevent inserting old (stale) data
			self.actionBar.resetLoadingState()
			return

		self._currentRequests.remove(req)
		data = NetworkService.decode(req)

		if req.node == self.rootNode:
			ol = self.entryFrame
		else:
			tmp = self.itemForKey(req.node)
			if not tmp:
				ol = self.entryFrame
			else:
				ol = tmp.ol

		for skel in data["skellist"]:
			if req.reqType == "leaf":
				hi = self.leafWidget(self.module, skel, data["structure"], self)
			else:
				hi = self.nodeWidget(self.module, skel, data["structure"], self)
			ol.appendChild(hi)
			if hi.data["key"] in self._expandedNodes:
				hi.toggleExpand()
				if not hi.childrenLoaded:
					hi.childrenLoaded = True
					self.loadNode(hi.data["key"])
		ol.sortChildren(self.getChildKey)

		if not ol._children and ol != self.entryFrame:
			ol.parent().addClass("has-no-child")

		if data["skellist"] and data["cursor"]:
			self.loadNode(req.node, data["cursor"])

		self.actionBar.resetLoadingState()

	def onDrop(self, event):
		"""
			We got a drop event. Make that item a direct child of our rootNode
		"""
		if event.target == self.element:  # only move if droped
			srcKey, skelType = event.dataTransfer.getData("Text").split("/")

			NetworkService.request(self.module, "move",
			                       {"skelType": skelType, "key": srcKey, "parentNode": self.rootNode}, secure=True,
			                       modifies=True)
			event.stopPropagation()

	def onDragOver(self, event):
		"""
			Allow dropping children on the rootNode
		"""
		event.preventDefault()
		event.stopPropagation()

	def getChildKey(self, widget):
		"""
			Order by sortindex
		"""
		name = float(widget.data.get("sortindex") or 0)
		return name

	def onSelectionChanged(self, widget, selection):
		return 0

	def activateCurrentSelection(self):
		conf["mainWindow"].removeWidget(self)

		if self.selectCallback:
			print([element.data for element in self.currentSelectedElements])
			self.selectCallback(self, [element.data for element in self.currentSelectedElements])

	@staticmethod
	def canHandle(moduleName, moduleInfo):
		return moduleInfo["handler"] == "tree" or moduleInfo["handler"].startswith("tree.")


moduleWidgetSelector.insert(1, TreeWidget.canHandle, TreeWidget)
displayDelegateSelector.insert(1, TreeWidget.canHandle, TreeWidget)


class BrowserLeafWidget(TreeLeafWidget):
	def setStyle(self):
		self["style"]["background-color"] = "#f7edd2"
		self["class"].append("hierarchy-item")
		self.additionalDropAreas()
		self.buildDescription()
	# self.toggleArrow()
	# self.EntryIcon()


class BrowserNodeWidget(TreeNodeWidget):
	def setStyle(self):
		self["class"].append("hierarchy-item")
		self.additionalDropAreas()
		self.buildDescription()
	# self.toggleArrow()
	# self.EntryIcon()


class BreadcrumbNodeWidget(TreeNodeWidget):
	def setStyle(self):
		# self[ "style" ][ "background-color" ] = "#f7edd2"
		self.buildDescription()
# self.toggleArrow()
# self.EntryIcon()


class TreeBrowserWidget(TreeWidget):
	leafWidget = BrowserLeafWidget
	nodeWidget = BrowserNodeWidget

	def __init__(self, module, rootNode=None, node=None, context=None, *args, **kwargs):
		super(TreeBrowserWidget, self).__init__(module, rootNode, node, context, *args, **kwargs)

	def rebuildPath(self):
		"""
			Rebuild the displayed path-list.
		"""
		self.pathList.removeAllChildren()

		NetworkService.request(
			self.module, "view/node/%s" % self.node,
			successHandler=self.onPathRequestSucceded
		)

	def onPathRequestSucceded(self, req):
		"""
			Rebuild the displayed path-list according to request data
		"""
		answ = NetworkService.decode(req)
		skel = answ["values"]

		if skel["parententry"] and skel["parententry"] != skel["key"]:
			c = BreadcrumbNodeWidget(self.module, skel, [], self)

			NetworkService.request(
				self.module, "view/node/%s" % skel["parententry"],
				successHandler=self.onPathRequestSucceded
			)

		else:
			c = BreadcrumbNodeWidget(self.module, {"key": self.rootNode, "name": "root"}, [], self)
			c.addClass("is-rootnode")

		self.pathList.prependChild(c)

	def breadcrumb(self):
		self.pathList = html5.Div()
		self.pathList.addClass("vi-tree-breadcrumb")
		self.appendChild(self.pathList)

	def onDblClick(self, event):
		for child in self.entryFrame.children():
			if html5.utils.doesEventHitWidgetOrChildren(event, child):
				if self.selectCallback:
					self.clearSelection()
					if self.extendSelection(child):
						self.activateCurrentSelection()

				elif isinstance(child, TreeNodeWidget):
					self.entryFrame.removeAllChildren()
					self.loadNode(child.data["key"])
					self.rebuildPath()

				break

	@staticmethod
	def canHandle(module, moduleInfo):
		return moduleInfo["handler"] == "tree.browser" or moduleInfo["handler"].startswith("tree.browser.")


moduleWidgetSelector.insert(1, TreeBrowserWidget.canHandle, TreeBrowserWidget)
displayDelegateSelector.insert(1, TreeBrowserWidget.canHandle, TreeBrowserWidget)
