#-*- coding: utf-8 -*-
from vi import html5

from vi.config import conf
from vi.i18n import translate
from vi.network import NetworkService
from vi.priorityqueue import viewDelegateSelector, moduleHandlerSelector
# from vi.sidebarwidgets.filterselector import CompoundFilter #fixme
#from vi.widgets.actionbar import ActionBar
from vi.widgets.sidebar import SideBar
from vi.framework.components.datatable import DataTable, ViewportDataTable
from vi.embedsvg import embedsvg
from vi.framework.components.actionbar import ActionBar


class ListWidget(html5.Div):
	"""
		Provides the interface to list-applications.
		It acts as a data-provider for a DataTable and binds an action-bar
		to this table.
	"""
	def __init__(self, module, filter=None, columns=None, selectMode = None, filterID=None, filterDescr=None,
	             batchSize = None, context = None, autoload = True, *args, **kwargs):
		"""
			:param module: Name of the module we shall handle. Must be a list application!
			:type module: str
		"""

		if not module in conf["modules"].keys():
			conf["mainWindow"].log("error", translate("The module '{module}' does not exist.", module=module))
			assert module in conf["modules"].keys()

		super(ListWidget, self).__init__()
		self.addClass("vi-widget vi-widget--list")
		self._batchSize = batchSize or conf["batchSize"]    # How many rows do we fetch at once?
		self.isDetaching = False #If set, this widget is beeing about to be removed - dont issue nextBatchNeeded requests
		self.module = module
		self.context = context

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
				print("fixme!")

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
		self.selectMode = selectMode
		assert selectMode in [None, "single", "multi"]

		if self.selectMode and filter is None and columns is None:
			#Try to select a reasonable set of cols / filter
			if conf["modules"] and module in conf["modules"].keys():
				tmpData = conf["modules"][module]
				if "columns" in tmpData.keys():
					columns = tmpData["columns"]
				if "filter" in tmpData.keys():
					filter = tmpData["filter"]

		self.filter = filter.copy() if isinstance(filter,dict) else {}
		self.columns = columns[:] if isinstance(columns,list) else []
		self.filterID = filterID #Hint for the sidebarwidgets which predefined filter is currently active
		self.filterDescr = filterDescr #Human-readable description of the current filter
		self._tableHeaderIsValid = False

		#build Table
		self.tableInitialization(*args, **kwargs)

		self.actionBar.setActions( self.getDefaultActions( myView ), widget=self )
		self.entryActionBar.setActions(self.getDefaultEntryActions(myView), widget=self)

		self.emptyNotificationDiv = html5.Div()
		svg = embedsvg.get("icons-error-file")
		if svg:
			self.emptyNotificationDiv.element.innerHTML = svg + self.emptyNotificationDiv.element.innerHTML

		self.emptyNotificationDiv.appendChild(html5.TextNode(translate("Currently no entries")))
		self.emptyNotificationDiv.addClass("popup popup--center popup--local msg emptynotification")
		self.widgetContent.appendChild(self.emptyNotificationDiv)
		self.emptyNotificationDiv.removeClass("is-active")

		self.setTableActionBar()
		if autoload:
			self.reloadData()

		self.sinkEvent("onClick")

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
		          "selectionActivatedEvent",
		          "cursorMovedEvent",
		          "tableChangedEvent",
		          "getCurrentSelection",
		          "requestingFinishedEvent"]:
			setattr(self, f, getattr(self.table, f))

		if self.selectMode:
			self.selectionActivatedEvent.register(self)

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

	def getDefaultActions(self, view = None ):
		"""
			Returns the list of actions available in our actionBar
		"""
		defaultActions = ["add", "selectfields"]

		if self.selectMode == "multi":
			defaultActions += ["|", "selectall", "unselectall", "selectinvert"]

		if self.selectMode:
			defaultActions += ["|", "select","close"]

		defaultActions += ["|",  "reload", "setamount", "intpreview", "selectfilter"] #"pagefind",  "loadnext",

		#if not self.selectMode:
		#	defaultActions += ["|", "exportcsv"]

		# Extended actions from view?
		if view and "actions" in view.keys():
			if defaultActions[-1] != "|":
				defaultActions.append( "|" )

			defaultActions.extend( view[ "actions" ] or [] )

		# Extended Actions from config?
		elif conf["modules"] and self.module in conf["modules"].keys():
			cfg = conf["modules"][ self.module ]

			if "actions" in cfg.keys() and cfg["actions"]:
				if defaultActions[-1] != "|":
					defaultActions.append( "|" )

				defaultActions.extend( cfg["actions"] )

		return defaultActions

	def getDefaultEntryActions(self, view = None ):
		"""
			Returns the list of actions available in our actionBar
		"""
		defaultActions = ["edit", "clone", "delete", "|", "preview"]

		# Extended actions from view?
		if view and "actions" in view.keys():
			if defaultActions[-1] != "|":
				defaultActions.append( "|" )

			defaultActions.extend( view[ "actions" ] or [] )

		# Extended Actions from config?
		elif conf["modules"] and self.module in conf["modules"].keys():
			cfg = conf["modules"][ self.module ]

			if "entryActions" in cfg.keys() and cfg["entryActions"]:
				if defaultActions[-1] != "|":
					defaultActions.append( "|" )

				defaultActions.extend( cfg["entryActions"] )

		return defaultActions

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
			filter["amount"] = self._batchSize
			filter["cursor"] = self._currentCursor

			self._currentRequests.append(NetworkService.request(self.module, "list", filter,
			                                successHandler=self.onCompletion, failureHandler=self.showErrorMsg,
			                                cacheable=True ) )
			self._currentCursor = None
		else:
			self.actionBar.resetLoadingState()
			self.entryActionBar.resetLoadingState()
			self.tableBottomActionBar.resetLoadingState()
			self.table.setDataProvider(None)

	def onAttach(self):
		super( ListWidget, self ).onAttach()
		NetworkService.registerChangeListener( self )

	def onDetach(self):
		self.isDetaching = True
		super( ListWidget, self ).onDetach()
		NetworkService.removeChangeListener( self )

	def onDataChanged(self, module, **kwargs):
		"""
			Refresh our view if element(s) in this module have changed
		"""
		if module and module != self.module:
			return

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
		filter["amount"] = self._batchSize

		self._currentRequests.append(
			NetworkService.request(self.module, "list", filter,
			                        successHandler=self.onCompletion,
			                        failureHandler=self.showErrorMsg,
			                        cacheable=True))

	def setFilter(self, filter, filterID=None, filterDescr=None):
		"""
			Applies a new filter.
		"""
		self.filter = filter
		self.filterID = filterID
		self.filterDescr = filterDescr
		self.reloadData()

	def setContext(self, context):
		"""
			Applies a new context.
		"""
		self.context = context
		self.reloadData()

	def getFilter(self):
		if self.filter:
			return( {k:v for k,v in self.filter.items()})
		return( {} )

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

		if data["structure"] is None:
			if self.table.getRowCount():
				# We cant load any more results
				self.targetPage = self.loadedPages #reset targetpage to maximum
				self.requestingFinishedEvent.fire()
				self.table.setDataProvider(None)
				self.table.onTableChanged(None, self.table.getRowCount())
			else:
				self.table["style"]["display"] = "none"
				self.emptyNotificationDiv.addClass("is-active")

			return

		self.table["style"]["display"] = ""
		self.emptyNotificationDiv.removeClass("is-active")
		self._structure = data["structure"]

		if not self._tableHeaderIsValid:
			if not self.columns:
				self.columns = []
				for boneName, boneInfo in data["structure"]:
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
		tmpDict = {key: bone for key, bone in self._structure}

		fields = [x for x in fields if x in tmpDict.keys()]
		self.columns = fields

		self.table.setShownFields(fields)

		for boneName in fields:
			boneInfo = tmpDict[boneName]
			delegateFactory = viewDelegateSelector.select( self.module, boneName, tmpDict )( self.module, boneName, tmpDict )
			self.table.setCellRender( boneName, delegateFactory )
			boneInfoList.append( boneInfo )

		if conf["showBoneNames"]:
			self.table.setHeader(fields)
		else:
			self.table.setHeader([x.get("descr", "") for x in boneInfoList])

		rendersDict = {}

		for boneName in fields:
			boneInfo = tmpDict[boneName]
			delegateFactory = viewDelegateSelector.select( self.module, boneName, tmpDict )( self.module, boneName, tmpDict )
			rendersDict[ boneName ] = delegateFactory
			boneInfoList.append( boneInfo )

		self.table.setCellRenders( rendersDict )
		self._tableHeaderIsValid = True

	def getFields(self):
		return( self.columns[:] )

	def onSelectionActivated(self, table, selection):
		conf["mainWindow"].removeWidget(self)

	def activateCurrentSelection(self):
		"""
			Emits the selectionActivated event if there's currently a selection
		"""
		self.table.activateCurrentSelection()

	@staticmethod
	def canHandle(moduleName, moduleInfo):
		return moduleInfo["handler"] == "list" or moduleInfo["handler"].startswith("list.")

	@staticmethod
	def render(moduleName, adminInfo, context=None):
		filter = adminInfo.get("filter")
		columns = adminInfo.get("columns")
		filterID = adminInfo.get("__id")
		filterDescr = adminInfo.get("visibleName", "")
		autoload = adminInfo.get("autoload", True)
		selectMode = adminInfo.get("selectMode")
		batchSize = adminInfo.get("batchSize", conf["batchSize"])

		return ListWidget(module=moduleName,
		                          filter=filter,
		                          filterID=filterID,
		                          selectMode=selectMode,
		                          batchSize=batchSize,
		                          columns=columns,
		                          context=context,
		                          autoload=autoload,
		                          filterDescr=filterDescr)

moduleHandlerSelector.insert(1, ListWidget.canHandle, ListWidget.render)


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

		if self.selectMode:
			self.selectionActivatedEvent.register(self)

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

		print("ZZZ")
		print(self.targetPage)
		print(self.loadedPages)


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
		return moduleInfo["handler"] == "list" or moduleInfo["handler"].startswith("list.")

	@staticmethod
	def render(moduleName, adminInfo, context=None):

		filter = adminInfo.get("filter")
		columns = adminInfo.get("columns")
		filterID = adminInfo.get("__id"),
		filterDescr = adminInfo.get("visibleName", ""),
		autoload = adminInfo.get("autoload", True)
		selectMode = adminInfo.get("selectMode")
		batchSize = adminInfo.get("batchSize",conf["batchSize"])

		return ViewportListWidget(module=moduleName,
		                          filter=filter,
		                          filterID=filterID,
		                          selectMode=selectMode,
		                          batchSize=batchSize,
		                          columns=columns,
		                          context=context,
		                          autoload=autoload,
		                          filterDescr=filterDescr)

moduleHandlerSelector.insert(-1 , ViewportListWidget.canHandle, ViewportListWidget.render)

