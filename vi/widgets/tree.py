# -*- coding: utf-8 -*-
from flare import html5, utils
from flare.viur.formatString import formatString
from flare.network import NetworkService
from vi.framework.components.actionbar import ActionBar
from flare.event import EventDispatcher
from vi.priorityqueue import DisplayDelegateSelector, ModuleWidgetSelector
from flare.viur import BoneSelector
from vi.config import conf
from flare.i18n import translate
from flare.icons import SvgIcon,Icon
from time import time
from collections import OrderedDict
import logging


from flare.viur.widgets.tree import TreeItemWidget,TreeLeafWidget, TreeNodeWidget


class TreeWidget(html5.Div):
	"""
	Base Widget that renders a tree.
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
		self.addClass("vi-widget vi-widget--hierarchy is-drop-target")
		self["tabindex"] = 1
		self.sinkEvent(
			"onKeyDown",
			"onKeyUp",
			"onDrop",
			"onDragOver"
		)

		self.module = module
		self.rootNode = rootNode
		self.node = node or rootNode
		self.context = context

		# Action bar
		self.actionBar = ActionBar(module, "tree")
		self.actionBar.setActions(self.getActions(), widget=self)
		self.appendChild(self.actionBar)

		# Entry frame
		self.entryFrame = html5.Ol()
		self.entryFrame.addClass("hierarchy")
		self.appendChild(self.entryFrame)

		# States
		self._isCtrlPressed = False
		self._isShiftPressed = False
		self._ctlStartRow = None
		self._currentRow = None
		self._expandedNodes = []
		self._currentRequests = []
		self.path = []

		# Selection
		self.selectionCallback = None
		self.selectionAllow = TreeItemWidget
		self.selectionMulti = False
		self.selection = []
		self.isSelector = False

		# Events
		self.selectionChangedEvent = EventDispatcher("selectionChanged")
		self.selectionActivatedEvent = EventDispatcher("selectionActivated")
		self.rootNodeChangedEvent = EventDispatcher("rootNodeChanged")
		self.nodeChangedEvent = EventDispatcher("nodeChanged")

		self.viewLeafStructure = None
		self.viewNodeStructure = None
		self.addLeafStructure = None
		self.addNodeStructure = None
		self.editStructure = None
		self.editLeafStructure = None
		self.editNodeStructure = None

		# Either load content or get root Nodes
		if self.rootNode:
			self.requestStructure()
		else:
			NetworkService.request(
				self.module,
				"listRootNodes",
				self.context or {},
				successHandler=self.onSetDefaultRootNode,
				failureHandler=self.showErrorMsg
			)

	def requestStructure( self ):
		NetworkService.request( None,
								"/vi/getStructure/%s" % self.module,
								successHandler = self.receivedStructure
								)
	def receivedStructure( self, resp ):
		data = NetworkService.decode(resp)
		for stype, structlist in data.items():
			structure = OrderedDict()
			for k, v in structlist:
				structure[k] = v
			if stype == "viewNodeSkel":
				self.viewNodeStructure = structure
			elif stype == "viewLeafSkel":
				self.viewLeafStructure = structure
			elif stype == "editNodeSkel":
				self.editNodeStructure = structure
			elif stype == "editLeafSkel":
				self.editLeafStructure = structure
			elif stype == "addNodeSkel":
				self.addNodeStructure = structure
			elif stype == "addLeafSkel":
				self.addLeafStructure = structure

		self.reloadData()


	def setSelector(self, callback, multi=True, allow=None):
		"""
		Configures the widget as selector for a relationalBone and shows it.
		"""
		self.isSelector = True
		self.selectionCallback = callback
		self.selectionAllow = allow or TreeItemWidget
		self.selectionMulti = multi

		self.actionBar.setActions(["select", "close", "|"] + self.getActions())
		conf["mainWindow"].stackWidget(self)

	def selectorReturn(self):
		"""
		Returns the current selection to the callback configured with `setSelector`.
		"""
		conf["mainWindow"].removeWidget(self)

		if self.selectionCallback:
			self.selectionCallback(self, [element.data for element in self.selection])

	def onKeyDown(self, event):
		if html5.isControl(event) or html5.getKey(event) == "Meta":
			self._isCtrlPressed = True

		elif html5.isShift(event):  # Shift
			self._isShiftPressed = True
			try:
				self._ctlStartRow = self._currentRow or self.selection[0]
			except:
				self._ctlStartRow = 0

	def onKeyUp(self, event):
		if html5.isControl(event) or html5.getKey(event) == "Meta":
			self._isCtrlPressed = False

		elif html5.isShift(event):
			self._isShiftPressed = False
			self._ctlStartRow = None




	def getActions(self):
		"""
		Returns a list of actions that are being set for the ActionBar.
		Override this to provide additional actions.
		"""
		return [
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
		]

	def clearSelection(self):
		"""
		Empties the current selection.
		"""
		for element in self.selection:
			element.removeClass("is-focused")

		self.selection.clear()

	def extendSelection(self, element):
		"""
		Extends the current selection to element.

		This is normally done by clicking or tabbing on an element.
		"""

		if not isinstance(element, self.selectionAllow):
			logging.warning("Element %r not allowed for selection", element)
			return False

		# Perform selection
		if self._isCtrlPressed and self.selectionMulti:
			if element in self.selection:
				self.selection.remove(element)
				element.removeClass("is-focused")
			else:
				self.selection.append(element)
				element.addClass("is-focused")
		elif self._isShiftPressed and self.selectionMulti:
			self.selection =  self.entryFrame._children[min(self.entryFrame._children.index(element),self._currentRow): max(self.entryFrame._children.index(element),self._currentRow)+1]

			for x in self.entryFrame._children:
				x.removeClass("is-focused")

			for x in self.selection:
				x.addClass("is-focused")

		else:
			self.clearSelection()
			self.selection.append(element)
			element.addClass("is-focused")

		if self.selectionMulti:
			self._currentRow = self.entryFrame._children.index(element)

		self.selectionChangedEvent.fire(self, self.selection)

	def activateSelection(self, element):
		"""
		Activates the current selection or element.

		An activation mostly is an action like selecting or editing an item.
		This is normally done by double-clicking an element.
		"""
		if self.selection:
			if self.selectionCallback:
				self.selectorReturn()
			else:
				self.selectionActivatedEvent.fire(self, self.selection)

	def requestChildren(self, element):
		self.loadNode(element.data["key"])

	def showErrorMsg(self, req=None, code=None):
		"""
			Removes all currently visible elements and displayes an error message
		"""
		self.actionBar.hide()
		self.entryFrame.hide()

		errorDiv = html5.Div()
		errorDiv.addClass("popup popup--center popup--local msg msg--error is-active error_msg")
		if code and (code == 401 or code == 403):
			txt = translate("Access denied!")
		else:
			txt = translate("Error {code} occurred!", code=code)

		errorDiv.addClass("error_code_%s" % (code or 0))  # fixme: not an ignite style?
		errorDiv.appendChild(html5.TextNode(txt))
		self.appendChild(errorDiv)

	def onDataChanged(self, module,*args, **kwargs):
		if module != self.module:
			isRootNode = False
			for k, v in conf["modules"].items():
				if (k == module
						and v.get("handler") == "list"
						and self.module in v.get("changeInvalidates", [])):
					isRootNode = True
					break

			if not isRootNode:
				return

		self.actionBar.widgets["selectrootnode"].update()

		if not self.viewNodeStructure:
			self.requestStructure()
		else:
			self.reloadData()

	def onAttach(self):
		super(TreeWidget, self).onAttach()
		NetworkService.registerChangeListener(self)

	def onDetach(self):
		super(TreeWidget, self).onDetach()
		#NetworkService.removeChangeListener(self)

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
		if not self.viewNodeStructure:
			self.requestStructure()
		else:
			self.reloadData()

	def reloadData(self):
		"""
			Reload the data were displaying.
		"""

		def collectExpandedNodes(currNode):
			res = []
			for c in currNode.children():
				if isinstance(c, TreeItemWidget):
					if c.isExpanded:
						res.append(c.data["key"])

					res.extend(collectExpandedNodes(c.ol))

			return res

		self._expandedNodes = collectExpandedNodes(self.entryFrame)
		self._currentRequests = []
		self.entryFrame.removeAllChildren()

		self.loadNode(self.rootNode)

	def loadNode(self, node, cursor=None, reqType=None, overrideParams=None):
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

		def nodeReq():
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

		def leafReq():
			if self.leafWidget:
				if cursor:
					params.update({"cursor": cursor})

				r = NetworkService.request(self.module, "list/leaf", params,
										   successHandler=self.onRequestSucceded,
										   failureHandler=self.showErrorMsg)
				r.reqType = "leaf"
				r.node = node
				self._currentRequests.append(r)

		if reqType == 'node':
			nodeReq()
		elif reqType == 'leaf':
			leafReq()
		else:
			nodeReq()
			leafReq()

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
				hi = self.leafWidget(self.module, skel, self.viewLeafStructure, self)
			else:
				hi = self.nodeWidget(self.module, skel, self.viewNodeStructure, self)
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
			self.loadNode(req.node, data["cursor"], req.reqType)

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

	@staticmethod
	def canHandle(moduleName, moduleInfo):
		return moduleInfo["handler"] == "tree" or moduleInfo["handler"].startswith("tree.")

ModuleWidgetSelector.insert(1, TreeWidget.canHandle, TreeWidget)
DisplayDelegateSelector.insert(1, TreeWidget.canHandle, TreeWidget)


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
		self.selectionMulti = True
		self.pathList = html5.Div()
		self.pathList.addClass("vi-tree-breadcrumb")
		self.appendChild(self.pathList, self.entryFrame)

	def reloadData(self):
		super().reloadData()
		self.rebuildPath()

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
			c = BreadcrumbNodeWidget(self.module, skel, {}, self)

			NetworkService.request(
				self.module, "view/node/%s" % skel["parententry"],
				successHandler=self.onPathRequestSucceded
			)

		else:
			c = BreadcrumbNodeWidget(self.module, {"key": self.rootNode, "name": "root"}, {}, self)
			c.addClass("is-rootnode")

		self.pathList.prependChild(c)

	def activateSelection(self, element):
		if isinstance(element, TreeNodeWidget):
			self.entryFrame.removeAllChildren()
			self.loadNode(element.data["key"])
			self.rebuildPath()
		else:
			super().activateSelection(element)

	@staticmethod
	def canHandle(module, moduleInfo):
		return moduleInfo["handler"] == "tree.browser" or moduleInfo["handler"].startswith("tree.browser.")

ModuleWidgetSelector.insert(5, TreeBrowserWidget.canHandle, TreeBrowserWidget)
DisplayDelegateSelector.insert(5, TreeBrowserWidget.canHandle, TreeBrowserWidget)
