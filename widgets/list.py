#-*- coding: utf-8 -*-
import html5
from config import conf
from i18n import translate
from network import NetworkService
from priorityqueue import viewDelegateSelector, moduleHandlerSelector
from sidebarwidgets.filterselector import CompoundFilter
from widgets.actionbar import ActionBar
from widgets.sidebar import SideBar
from widgets.table import DataTable


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
		self._batchSize = batchSize or conf["batchSize"]    # How many rows do we fetch at once?
		self.isDetaching = False #If set, this widget is beeing about to be removed - dont issue nextBatchNeeded requests
		self.module = module
		self.context = context

		self.actionBar = ActionBar(module, "list", currentAction="list")
		self.appendChild( self.actionBar )

		self.sideBar = SideBar()
		self.appendChild( self.sideBar )

		myView = None

		if filterID:
			if conf["modules"] and module in conf["modules"].keys():
				if "views" in conf["modules"][ module].keys() and conf["modules"][ module]["views"]:
					for v in conf["modules"][ module]["views"]:
						if v["__id"] == filterID:
							myView = v
							break
			if myView and "extendedFilters" in myView.keys() and myView["extendedFilters"]:
				self.appendChild(CompoundFilter(myView, module, embed=True))

		checkboxes = (conf["modules"]
		              and module in conf["modules"].keys()
		              and "checkboxSelection" in conf["modules"][module].keys()
		              and conf["modules"][module]["checkboxSelection"])
		indexes = (conf["modules"]
		           and module in conf["modules"].keys()
		           and "indexes" in conf["modules"][module].keys()
		           and conf["modules"][module]["indexes"])

		self.table = DataTable( checkboxes=checkboxes, indexes=indexes, *args, **kwargs )
		self.appendChild( self.table )
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

		self.table.setDataProvider(self)
		self.filter = filter.copy() if isinstance(filter,dict) else {}
		self.columns = columns[:] if isinstance(columns,list) else []
		self.filterID = filterID #Hint for the sidebarwidgets which predefined filter is currently active
		self.filterDescr = filterDescr #Human-readable description of the current filter
		self._tableHeaderIsValid = False

		#Proxy some events and functions of the original table
		for f in ["selectionChangedEvent",
		            "selectionActivatedEvent",
		            "cursorMovedEvent",
					"tableChangedEvent",
		            "getCurrentSelection"]:
			setattr( self, f, getattr(self.table,f))

		self.actionBar.setActions( self.getDefaultActions( myView ) )

		if self.selectMode:
			self.selectionActivatedEvent.register(self)

		self.emptyNotificationDiv = html5.Div()
		self.emptyNotificationDiv.appendChild(html5.TextNode(translate("Currently no entries")))
		self.emptyNotificationDiv["class"].append("emptynotification")
		self.appendChild(self.emptyNotificationDiv)
		self.emptyNotificationDiv["style"]["display"] = "none"
		self.table["style"]["display"] = "none"
		self.filterDescriptionSpan = html5.Span()
		self.appendChild( self.filterDescriptionSpan )
		self.filterDescriptionSpan["class"].append("filterdescription")
		self.updateFilterDescription()

		if autoload:
			self.reloadData()

	def updateFilterDescription(self):
		self.filterDescriptionSpan.removeAllChildren()

		if self.filterDescr:
			self.filterDescriptionSpan.appendChild(html5.TextNode(html5.utils.unescape(self.filterDescr)))

	def getDefaultActions(self, view = None ):
		"""
			Returns the list of actions available in our actionBar
		"""
		defaultActions = ["add", "edit", "clone", "delete", "|", "preview", "selectfields"]

		if self.selectMode == "multi":
			defaultActions += ["|", "selectall", "unselectall", "selectinvert"]

		if self.selectMode:
			defaultActions += ["|", "select","close"]

		defaultActions += ["|", "reload","selectfilter"]

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

	def showErrorMsg(self, req=None, code=None):
		"""
			Removes all currently visible elements and displayes an error message
		"""
		self.actionBar["style"]["display"] = "none"
		self.table["style"]["display"] = "none"
		errorDiv = html5.Div()
		errorDiv["class"].append("error_msg")
		if code and (code==401 or code==403):
			txt = translate("Access denied!")
		else:
			txt = translate("An unknown error occurred!")
		errorDiv["class"].append("error_code_%s" % (code or 0))
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
		self.updateFilterDescription()
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

		self._currentRequests.remove( req )
		self.actionBar.resetLoadingState()

		data = NetworkService.decode( req )

		if data["structure"] is None:
			if self.table.getRowCount():
				self.table.setDataProvider(None) #We cant load any more results
			else:
				self.table["style"]["display"] = "none"
				self.emptyNotificationDiv["style"]["display"] = ""
				#self.element.innerHTML = "<center><strong>Keine Ergebnisse</strong></center>"
			return

		self.table["style"]["display"] = ""
		self.emptyNotificationDiv["style"]["display"] = "none"
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
			self.table.setDataProvider(None)

		self.table.extend( data["skellist"] )

	def setFields(self, fields):
		if not self._structure:
			self._tableHeaderIsValid = False
			return

		boneInfoList = []
		tmpDict = {key: bone for key, bone in self._structure}

		fields = [x for x in fields if x in tmpDict.keys()]
		self.columns = fields

		for boneName in fields:
			boneInfo = tmpDict[boneName]
			delegateFactory = viewDelegateSelector.select( self.module, boneName, tmpDict )( self.module, boneName, tmpDict )
			self.table.setCellRender( boneName, delegateFactory )
			boneInfoList.append( boneInfo )

		if conf["showBoneNames"]:
			self.table.setHeader(fields)
		else:
			self.table.setHeader([x.get("descr", "") for x in boneInfoList])

		self.table.setShownFields(fields)
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
	def render(moduleName, adminInfo, context):

		filter = adminInfo.get("filter")
		columns = adminInfo.get("columns")

		return ListWidget(module=moduleName, filter=filter, columns=columns, context=context)

moduleHandlerSelector.insert(1, ListWidget.canHandle, ListWidget.render)
