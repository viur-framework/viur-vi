from flare import html5
from collections import defaultdict

from vi.config import conf
from flare.i18n import translate
from flare.network import NetworkService
from vi.priorityqueue import moduleWidgetSelector
from flare.forms import boneSelector
from vi.widgets.sidebar import SideBar
from vi.framework.components.datatable import DataTable, ViewportDataTable
from vi.framework.components.actionbar import ActionBar
from flare.event import EventDispatcher
from flare.icons import SvgIcon
from collections import OrderedDict

import logging


class ListWidget(html5.Div):
	"""
		Provides the interface to list-applications.
		It acts as a data-provider for a DataTable and binds an action-bar
		to this table.
	"""
	def __init__(self, module, filter=None, columns=None, filterID=None, filterDescr=None,
	             batchSize = None, context = None, autoload = True, *args, **kwargs):
		"""
			:param module: Name of the module we shall handle. Must be a list application!
			:type module: str
		"""

		if not module in conf["modules"].keys():
			conf["mainWindow"].log("error", translate("The module '{{module}}' does not exist.", module=module))
			assert module in conf["modules"].keys()

		super(ListWidget, self).__init__()
		self.addClass("vi-widget vi-widget--list")
		self["style"]["height"] = "100%"
		self._batchSize = batchSize or conf["batchSize"]    # How many rows do we fetch at once?
		self.isDetaching = False #If set, this widget is beeing about to be removed - dont issue nextBatchNeeded requests
		self.module = module
		self.context = context
		self.isSelector = False

		self.loadedPages = 0  # Amount of Pages which are currently loaded
		self.currentPage = self.loadedPages  # last loaded page
		self.targetPage = 1 #the page which we want to show next if we set this to currentPage +1 and call setPage next page will be loaded

		#List actions
		self.actionBar = ActionBar(module, "list", currentAction="list")
		self.appendChild( self.actionBar )

		#Entry Actions
		self.entryActionBar = ActionBar(module,"list", currentAction = "list")
		self.entryActionBar["class"] = ["bar", "vi-entryactionbar"]
		self.appendChild( self.entryActionBar )

		self.sideBar = SideBar()
		self.appendChild( self.sideBar )

		self.widgetContent = html5.Div()
		self.widgetContent.addClass("vi-widget-content")
		self.appendChild(self.widgetContent)

		myView = None

		if filterID:
			if conf["modules"] and module in conf["modules"].keys():
				if "views" in conf["modules"][ module].keys() and conf["modules"][ module]["views"]:
					for v in conf["modules"][ module]["views"]:
						if v["__id"] == filterID:
							myView = v
							break
			if myView and "extendedFilters" in myView.keys() and myView["extendedFilters"]:

				#fixme
				#self.appendChild(CompoundFilter(myView, module, embed=True))
				logging.error("#fixme CompoundFilter")

		self._checkboxes = (conf["modules"]
		              and module in conf["modules"].keys()
		              and "checkboxSelection" in conf["modules"][module].keys()
		              and conf["modules"][module]["checkboxSelection"])
		self._indexes = (conf["modules"]
		           and module in conf["modules"].keys()
		           and "indexes" in conf["modules"][module].keys()
		           and conf["modules"][module]["indexes"])

		self._currentCursor = None
		self._structure = None
		self._currentRequests = []
		self.columns = []

		self.selectionMulti = True
		self.selectionAllow = None
		self.selectionCallback = None

		self.filter = filter.copy() if isinstance(filter, dict) else {}
		self.columns = columns[:] if isinstance(columns, list) else []
		self.filterID = filterID #Hint for the sidebarwidgets which predefined filter is currently active
		self.filterDescr = filterDescr #Human-readable description of the current filter
		self._tableHeaderIsValid = False

		#build Table
		self.tableInitialization(*args, **kwargs)
		self.selectionActivatedEvent = EventDispatcher("selectionActivated")

		self.actionBar.setActions(self.getActions(myView), widget=self)
		self.entryActionBar.setActions(self.getDefaultEntryActions(myView), widget=self)

		self.emptyNotificationDiv = html5.Div()
		self.emptyNotificationDiv.prependChild( SvgIcon( "icon-error-file", title = "Currently no entries" ) )

		self.emptyNotificationDiv.appendChild(html5.TextNode(translate("Currently no entries")))
		self.emptyNotificationDiv.addClass("popup popup--center popup--local msg emptynotification")
		self.widgetContent.appendChild(self.emptyNotificationDiv)
		self.emptyNotificationDiv.removeClass("is-active")

		self.viewStructure = None
		self.editStructure = None
		self.addStructure = None

		self.setTableActionBar()

		if autoload:
			self.requestStructure()

		self.sinkEvent("onClick")

	def setSelector(self, callback, multi=True, allow=None):
		"""
		Configures the widget as selector for a relationalBone and shows it.
		"""
		self.isSelector = True
		self.selectionCallback = callback
		self.selectionMulti = multi

		if allow:
			logging.warning("allow is not implemented for List")

		actions = ["select", "close", "|"]

		if multi:
			actions += ["selectall", "unselectall", "selectinvert", "|"]

		self.actionBar.setActions(actions + self.getActions())
		conf["mainWindow"].stackWidget(self)

	def selectorReturn(self):
		"""
		Returns the current selection to the callback configured with `setSelector`.
		"""
		conf["mainWindow"].removeWidget(self)

		if self.selectionCallback:
			self.selectionCallback(self, self.getCurrentSelection())

	def tableInitialization(self,*args,**kwargs):
		'''
		Instantiates the table
		:param args: ListWidget Parameter
		:param kwargs: ListWidget Parameter
		:return:
		'''

		self.table = DataTable(checkboxes=self._checkboxes, indexes=self._indexes, *args, **kwargs)
		self.widgetContent.appendChild(self.table)
		self.table.setDataProvider(self)

		# Proxy some events and functions of the original table
		for f in ["selectionChangedEvent",
		          "cursorMovedEvent",
		          "tableChangedEvent",
		          "getCurrentSelection",
		          "requestingFinishedEvent"]:
			setattr(self, f, getattr(self.table, f))

		self.table.selectionActivatedEvent.register(self)
		self.requestingFinishedEvent.register(self)

		self.table["style"]["display"] = "none"

	def setAmount(self,amount):
		self._batchSize=amount

	def setPage(self,page = 0):
		'''
		sets targetpage. if not enougth loadedpages this pages will be requested
		:param page: sets targetpage
		:return:
		'''

		self.targetPage = self.currentPage+page

		if self.targetPage > self.loadedPages:
			self.onNextBatchNeeded()

	def onRequestingFinished(self,*args,**kwargs):
		pass

	def onClick(self, event):
		if event.target == self.table.element:
			self.table.table.unSelectAll()

	def setTableActionBar(self):
		self.tableBottomActionBar = ActionBar(self.module, "list", currentAction="list")
		self.appendChild(self.tableBottomActionBar)
		self.tableBottomActionBar.setActions(["|","loadnext", "|", "tableitems"]) #,"tableprev","tablenext"

	def getActions(self, view = None):
		"""
			Returns the list of actions available in the action bar.
		"""
		actions = ["add", "selectfields"]

		#if not self.selectMode:
		#	actions += ["|", "exportcsv"]

		# Extended actions from view?
		if view and "actions" in view.keys():
			if actions[-1] != "|":
				actions.append( "|" )

			actions.extend( view[ "actions" ] or [] )

		# Extended Actions from config?
		elif conf["modules"] and self.module in conf["modules"].keys():
			cfg = conf["modules"][ self.module ]

			if "actions" in cfg.keys() and cfg["actions"]:
				if actions[-1] != "|":
					actions.append( "|" )

				actions.extend( cfg["actions"] )

		actions += ["|",  "reload", "setamount", "intpreview", "selectfilter"] #"pagefind",  "loadnext",

		return actions

	def getDefaultEntryActions(self, view = None ):
		"""
			Returns the list of actions available in our actionBar
		"""
		actions = ["edit", "clone", "delete"]

		# Extended actions from view?
		if view and "actions" in view.keys():
			if actions[-1] != "|":
				actions.append( "|" )

			actions.extend( view[ "actions" ] or [] )

		# Extended Actions from config?
		elif conf["modules"] and self.module in conf["modules"].keys():
			cfg = conf["modules"][ self.module ]

			if "entryActions" in cfg.keys() and cfg["entryActions"]:
				#if actions[-1] != "|":
				#	actions.append( "|" )

				actions.extend( cfg["entryActions"] )
		actions.extend(["|", "preview"])
		return actions

	def showErrorMsg(self, req=None, code=None):
		"""
			Removes all currently visible elements and displayes an error message
		"""
		self.actionBar["style"]["display"] = "none"
		self.table["style"]["display"] = "none"
		errorDiv = html5.Div()
		errorDiv.addClass("popup popup--center popup--local msg msg--error is-active error_msg")
		if code and (code==401 or code==403):
			txt = translate("Access denied!")
		else:
			txt = translate("An unknown error occurred!")
		errorDiv.addClass("error_code_%s" % (code or 0))
		errorDiv.appendChild( html5.TextNode( txt ) )
		self.appendChild( errorDiv )

	def onNextBatchNeeded(self):
		"""
			Requests the next rows from the server and feed them to the table.
		"""
		if self._currentCursor and not self.isDetaching:
			filter = {}

			if self.context:
				filter.update(self.context)

			filter.update(self.filter)
			filter["limit"] = self._batchSize
			filter["cursor"] = self._currentCursor

			self._currentRequests.append(NetworkService.request(self.module, "list", filter,
			                                successHandler=self.onCompletion, failureHandler=self.showErrorMsg) )
			self._currentCursor = None
		else:
			self.actionBar.resetLoadingState()
			self.entryActionBar.resetLoadingState()
			self.tableBottomActionBar.resetLoadingState()
			self.table.setDataProvider(None)

	def onAttach(self):
		super(ListWidget, self).onAttach()
		NetworkService.registerChangeListener( self )

	def onDetach(self):
		self.isDetaching = True
		super(ListWidget, self).onDetach()
		#NetworkService.removeChangeListener( self )

	def onDataChanged(self, module, **kwargs):
		"""
			Refresh our view if element(s) in this module have changed
		"""

		if module and module != self.module:
			return
		if not self.viewStructure:
			self.requestStructure()
		else:
			self.reloadData()

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
			if stype == "viewSkel":
				self.viewStructure = structure
			elif stype == "editSkel":
				self.editStructure = structure
			elif stype == "addSkel":
				self.addStructure = structure

		self.reloadData()

	def reloadData(self):
		"""
			Removes all currently displayed data and refetches the first batch from the server.
		"""
		self.table.clear()
		self.loadedPages = 0
		self.targetPage = 1
		self.currentPage = 0
		self._currentCursor = None
		self._currentRequests = []

		filter = {}
		if self.context:
			filter.update(self.context)

		filter.update(self.filter)
		filter["limit"] = self._batchSize

		self._currentRequests.append(
			NetworkService.request(self.module, "list", filter,
			                        successHandler=self.onCompletion,
			                        failureHandler=self.showErrorMsg))

	def setFilter(self, filter, filterID=None, filterDescr=None):
		"""
			Applies a new filter.
		"""
		self.filter = filter
		self.filterID = filterID
		self.filterDescr = filterDescr
		if not self.viewStructure:
			self.requestStructure()
		else:
			self.reloadData()

	def setContext(self, context):
		"""
			Applies a new context.
		"""
		self.context = context
		if not self.viewStructure:
			self.requestStructure()
		else:
			self.reloadData()

	def getFilter(self):
		if self.filter:
			return {k:v for k,v in self.filter.items()}
		return {}

	def updateEmptyNotification( self ):
		pass

	def onCompletion(self, req):
		"""
			Pass the rows received to the datatable.
			:param req: The network request that succeed.
		"""
		if not req in self._currentRequests:
			return

		self.loadedPages +=1
		self.currentPage = self.loadedPages

		self._currentRequests.remove( req )
		self.actionBar.resetLoadingState()
		self.entryActionBar.resetLoadingState()
		self.tableBottomActionBar.resetLoadingState()

		data = NetworkService.decode( req )

		if not data["skellist"]:
			if self.table.getRowCount():
				# We cant load any more results
				self.targetPage = self.loadedPages #reset targetpage to maximum
				self.requestingFinishedEvent.fire()
				self.table.setDataProvider(None)
				self.table.onTableChanged(None, self.table.getRowCount())
			else:
				self.table["style"]["display"] = "none"
				self.emptyNotificationDiv.addClass("is-active")
				self.updateEmptyNotification()
			return

		self.table["style"]["display"] = ""
		self.emptyNotificationDiv.removeClass("is-active")
		self._structure = self.viewStructure
		#print(self.viewStructure)
		if not self._tableHeaderIsValid:
			if not self.columns:
				self.columns = []
				for boneName, boneInfo in self.viewStructure.items():
					if boneInfo["visible"]:
						self.columns.append( boneName )
			self.setFields( self.columns )

		if data["skellist"] and "cursor" in data.keys():
			self._currentCursor = data["cursor"]
			self.table.setDataProvider(self)
		else:
			self.requestingFinishedEvent.fire()
			self.table.setDataProvider(None)

		self.table.extend( data["skellist"], writeToModel =True )

		#if targetPage higher than loadedPage, request next Batch
		if self.targetPage > self.loadedPages:
			self.onNextBatchNeeded()

	def setFields(self, fields):
		if not self._structure:
			self._tableHeaderIsValid = False
			return

		boneInfoList = []
		tmpDict = {key: bone for key, bone in self._structure.items()}

		fields = [x for x in fields if x in tmpDict.keys()]
		self.columns = fields

		for boneName in fields:
			boneInfo = tmpDict[boneName]
			boneFactory = boneSelector.select(self.module, boneName, tmpDict)(self.module, boneName, tmpDict, defaultdict(list))
			self.table.setCellRender(boneName, boneFactory)
			boneInfoList.append( boneInfo )

		self.table.setShownFields( fields )

		if conf["showBoneNames"]:
			self.table.setHeader(fields)
		else:
			self.table.setHeader([x.get("descr", "") for x in boneInfoList])

		rendersDict = {}

		for boneName in fields:
			boneInfo = tmpDict[boneName]
			boneFactory = boneSelector.select(self.module, boneName, tmpDict)(self.module, boneName, tmpDict, defaultdict(list))
			rendersDict[boneName] = boneFactory
			boneInfoList.append(boneInfo)

		self.table.setCellRenders( rendersDict )
		self._tableHeaderIsValid = True

	def getFields(self):
		return self.columns[:]

	def onSelectionActivated(self, table, selection):
		self.activateSelection()

	def activateSelection(self):
		selection = self.getCurrentSelection()
		if selection:
			if self.selectionCallback:
				self.selectorReturn()
			else:
				self.selectionActivatedEvent.fire(self, selection)

	@staticmethod
	def canHandle(moduleName, moduleInfo):
		return moduleInfo["handler"] == "list" or moduleInfo["handler"].startswith("list.")

moduleWidgetSelector.insert(1, ListWidget.canHandle, ListWidget)


class ViewportListWidget(ListWidget):

	def tableInitialization(self,*args,**kwargs):
		'''
		Instantiates the table
		:param args: ListWidget Parameter
		:param kwargs: ListWidget Parameter

		Override explanation
			- use ViewPort DataTable with rows parameter
		'''
		self.table = ViewportDataTable(rows=self._batchSize,
		                               checkboxes=self._checkboxes,
		                               indexes=self._indexes,
		                               *args, **kwargs)
		self.widgetContent.appendChild(self.table)
		self.table.setDataProvider(self)

		# Proxy some events and functions of the original table
		for f in ["selectionChangedEvent",
		          "selectionActivatedEvent",
		          "cursorMovedEvent",
		          "tableChangedEvent",
		          "getCurrentSelection",
		          "requestingFinishedEvent"]:
			setattr(self, f, getattr(self.table, f))

		self.requestingFinishedEvent.register(self)

		self.table["style"]["display"] = "none"

	def setAmount(self,amount):
		self._batchSize = amount
		self.table._rows = amount
		self.table.rebuildTable()

	def setPage(self, page=0):
		'''
		sets targetpage. if not enougth loadedpages this pages will be requested
		else

		:param page: sets targetpage
		:return:
		'''

		self.targetPage = self.currentPage + page
		if self.targetPage<0:
			self.targetPage = 0

		if self.targetPage > self.loadedPages:
			self.onNextBatchNeeded()
			return  # waiting till pages loaded

		# if pages are existing load page
		self._setPage(self.targetPage)

	def _setPage(self, page=0):
		'''
		render page to table
		:param page:
		:return:
		'''
		if page > self.loadedPages:  # set page to Max possible
			page = self.loadedPages
		elif page<0:
			page = 0

		start = page * self._batchSize
		end = (page + 1) * self._batchSize

		objs = self.table._model[start:end]
		self.currentPage = max(page,1)
		self.table.update(objs,writeToModel=False)

	def onRequestingFinished(self,*args,**kwargs):
		#after Page is loaded scroll to this Page, while targetPage is lower than loadedPages
		if self.targetPage and self.targetPage < self.loadedPages:
			self._setPage(self.targetPage)

	def setTableActionBar(self):
		self.tableBottomActionBar = ActionBar(self.module, "list", currentAction="list")
		self.appendChild(self.tableBottomActionBar)
		self.tableBottomActionBar.setActions(["|","tableprev","loadnext","tablenext", "|", "tableitems"], widget=self)

	@staticmethod
	def canHandle(moduleName, moduleInfo):
		return moduleInfo["handler"] == "list.viewport" or moduleInfo["handler"].startswith("list.viewport.")


moduleWidgetSelector.insert(10, ViewportListWidget.canHandle, ViewportListWidget)

