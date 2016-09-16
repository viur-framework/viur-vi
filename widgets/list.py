#-*- coding: utf-8 -*-
import pyjd # this is dummy in pyjs.
import json
from config import conf
from network import NetworkService
from priorityqueue import viewDelegateSelector
from widgets.table import DataTable
from widgets.actionbar import ActionBar
from widgets.sidebar import SideBar
import html5
from sidebarwidgets.filterselector import CompoundFilter
from i18n import translate


class ListWidget( html5.Div ):
	"""
		Provides the interface to list-applications.
		It acts as a data-provider for a DataTable and binds an action-bar
		to this table.
	"""
	def __init__( self, modul, filter=None, columns=None, isSelector=False, filterID=None, filterDescr=None,
	                batchSize = None, *args, **kwargs ):
		"""
			@param modul: Name of the modul we shall handle. Must be a list application!
			@type modul: string
		"""
		if not modul in conf["modules"].keys():
			conf["mainWindow"].log("error", translate("The module '{module}' does not exist.", module=modul))
			assert modul in conf["modules"].keys()

		super( ListWidget, self ).__init__(  )
		self._batchSize = batchSize or conf["batchSize"]    # How many rows do we fetch at once?
		self.isDetaching = False #If set, this widget is beeing about to be removed - dont issue nextBatchNeeded requests
		self.modul = modul
		self.actionBar = ActionBar( modul, "list", currentAction="list" )
		self.appendChild( self.actionBar )
		self.sideBar = SideBar()
		self.appendChild( self.sideBar )

		myView = None

		if filterID:
			if conf["modules"] and modul in conf["modules"].keys():
				if "views" in conf["modules"][ modul ].keys() and conf["modules"][ modul ]["views"]:
					for v in conf["modules"][ modul ]["views"]:
						if v["__id"] == filterID:
							myView = v
							break
			if myView and "extendedFilters" in myView.keys() and myView["extendedFilters"]:
				self.appendChild( CompoundFilter(myView, modul, embed=True))

		checkboxes = (conf["modules"]
		                and modul in conf["modules"].keys()
						and "checkboxSelection" in conf["modules"][modul].keys()
		                and conf["modules"][modul]["checkboxSelection"])
		indexes = (conf["modules"]
		            and modul in conf["modules"].keys()
					and "indexes" in conf["modules"][modul].keys()
		            and conf["modules"][modul]["indexes"])

		self.table = DataTable( checkboxes=checkboxes, indexes=indexes, *args, **kwargs )
		self.appendChild( self.table )
		self._currentCursor = None
		self._structure = None
		self._currentRequests = []
		self.columns = []

		if isSelector and filter is None and columns is None:
			#Try to select a reasonable set of cols / filter
			if conf["modules"] and modul in conf["modules"].keys():
				tmpData = conf["modules"][modul]
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
		self.isSelector = isSelector

		#Proxy some events and functions of the original table
		for f in ["selectionChangedEvent",
		            "selectionActivatedEvent",
		            "cursorMovedEvent",
					"tableChangedEvent",
		            "getCurrentSelection"]:
			setattr( self, f, getattr(self.table,f))

		self.actionBar.setActions( self.getDefaultActions( myView ) )

		if isSelector:
			self.selectionActivatedEvent.register( self )

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
		self.reloadData()

	def updateFilterDescription(self):
		self.filterDescriptionSpan.removeAllChildren()

		if self.filterDescr:
			self.filterDescriptionSpan.appendChild(html5.TextNode(html5.utils.unescape(self.filterDescr)))

	def getDefaultActions(self, view = None ):
		"""
			Returns the list of actions available in our actionBar
		"""
		defaultActions = ["add", "edit", "clone", "delete",
		                  "|", "preview", "selectfields"]\
		                 + (["|", "select","close"] if self.isSelector else [])+["|", "reload","selectfilter","|", "exportcsv"]

		# Extended actions from view?
		if view and "actions" in view.keys():
			if defaultActions[-1] != "|":
				defaultActions.append( "|" )

			defaultActions.extend( view[ "actions" ] or [] )

		# Extended Actions from config?
		elif conf["modules"] and self.modul in conf["modules"].keys():
			cfg = conf["modules"][ self.modul ]

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
			filter = self.filter.copy()
			filter["amount"] = self._batchSize
			filter["cursor"] = self._currentCursor
			self._currentRequests.append( NetworkService.request(self.modul, "list", filter,
			                                successHandler=self.onCompletion, failureHandler=self.showErrorMsg,
			                                    cacheable=True ) )
			self._currentCursor = None
		else:
			self.table.setDataProvider( None )

	def onAttach(self):
		super( ListWidget, self ).onAttach()
		NetworkService.registerChangeListener( self )

	def onDetach(self):
		self.isDetaching = True
		super( ListWidget, self ).onDetach()
		NetworkService.removeChangeListener( self )

	def onDataChanged(self, module, **kwargs):
		"""
			Refresh our view if element(s) in this modul have changed
		"""
		if module and module != self.modul:
			return

		self.reloadData()

	def reloadData(self):
		"""
			Removes all currently displayed data and refetches the first batch from the server.
		"""
		self.table.clear()
		self._currentCursor = None
		self._currentRequests = []
		filter = self.filter.copy()
		filter["amount"] = self._batchSize

		self._currentRequests.append(
			NetworkService.request( self.modul, "list", filter,
			                        successHandler=self.onCompletion,
			                        failureHandler=self.showErrorMsg,
			                        cacheable=True ) )

	def setFilter(self, filter, filterID=None, filterDescr=None):
		"""
			Applies a new filter.
		"""
		self.filter = filter
		self.filterID = filterID
		self.filterDescr = filterDescr
		self.updateFilterDescription()
		self.reloadData()

	def getFilter(self):
		if self.filter:
			return( {k:v for k,v in self.filter.items()})
		return( {} )

	def onCompletion(self, req):
		"""
			Pass the rows received to the datatable.
			@param req: The network request that succeed.
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
		tmpDict = {}

		for key, bone in data["structure"]:
			tmpDict[ key ] = bone

		if not self._tableHeaderIsValid:
			if not self.columns:
				self.columns = []
				for boneName, boneInfo in data["structure"]:
					if boneInfo["visible"]:
						self.columns.append( boneName )
			self.setFields( self.columns )


		if "cursor" in data.keys():
			self._currentCursor = data["cursor"]
			self.table.setDataProvider( self )

		self.table.extend( data["skellist"] )

	def setFields(self, fields):
		if not self._structure:
			self._tableHeaderIsValid = False
			return

		boneInfoList = []
		tmpDict = {}

		for key, bone in self._structure:
			tmpDict[ key ] = bone

		fields = [x for x in fields if x in tmpDict.keys()]
		self.columns = fields

		for boneName in fields:
			boneInfo = tmpDict[boneName]
			delegateFactory = viewDelegateSelector.select( self.modul, boneName, tmpDict )( self.modul, boneName, tmpDict )
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
			delegateFactory = viewDelegateSelector.select( self.modul, boneName, tmpDict )( self.modul, boneName, tmpDict )
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
