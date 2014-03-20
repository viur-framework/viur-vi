import pyjd # this is dummy in pyjs.
import json
from config import conf
from network import NetworkService
from priorityqueue import viewDelegateSelector
from widgets.table import DataTable
from widgets.actionbar import ActionBar
from widgets.search import Search
from widgets.sidebar import SideBar
import html5




class ListWidget( html5.Div ):
	"""
		Provides the interface to list-applications.
		It acts as a dataprovider for a DataTable and binds an actionbar
		to this table.

	"""
	_batchSize = 20  #How many row we fetch at once
	def __init__( self, modul, filter=None, columns=None, isSelector=False, *args, **kwargs ):
		"""
			@param modul: Name of the modul we shall handle. Must be a list application!
			@type modul: string
		"""
		super( ListWidget, self ).__init__(  )
		self.modul = modul
		self.actionBar = ActionBar( modul, "list", currentAction="list" )
		self.appendChild( self.actionBar )
		self.sideBar = SideBar()
		self.appendChild( self.sideBar )
		self.table = DataTable()
		self.appendChild( self.table )
		self._currentCursor = None
		#self._currentSearchStr = None
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
		self._tableHeaderIsValid = False
		self.isSelector = isSelector
		#Proxy some events and functions of the original table
		for f in ["selectionChangedEvent","selectionActivatedEvent","cursorMovedEvent","getCurrentSelection"]:
			setattr( self, f, getattr(self.table,f))
		self.actionBar.setActions( self.getDefaultActions() )
		if isSelector:
			self.selectionActivatedEvent.register( self )
		self.emptyNotificationDiv = html5.Div()
		self.emptyNotificationDiv.appendChild(html5.TextNode("Currently no entries"))
		self.emptyNotificationDiv["class"].append("emptynotification")
		self.appendChild(self.emptyNotificationDiv)
		#self.search = Search()
		#self.appendChild(self.search)
		#self.search.startSearchEvent.register( self )
		self.emptyNotificationDiv["style"]["display"] = "none"
		self.table["style"]["display"] = "none"
		self.reloadData()

	def getDefaultActions(self):
		"""
			Returns the list of actions available in our actionBar
		"""
		return( ["add", "edit", "delete", "preview", "selectfields"]+(["select","close"] if self.isSelector else [])+["reload","selectfilter"] )

	def showErrorMsg(self, req=None, code=None):
		"""
			Removes all currently visible elements and displayes an error message
		"""
		self.actionBar["style"]["display"] = "none"
		self.table["style"]["display"] = "none"
		#self.search["style"]["display"] = "none"
		errorDiv = html5.Div()
		errorDiv["class"].append("error_msg")
		if code and (code==401 or code==403):
			txt = "Access denied!"
		else:
			txt = "An unknown error occurred!"
		errorDiv["class"].append("error_code_%s" % (code or 0))
		errorDiv.appendChild( html5.TextNode( txt ) )
		self.appendChild( errorDiv )

	#def onStartSearch(self, searchTxt):
	#	self._currentSearchStr = searchTxt
	#	self.reloadData()

	def onNextBatchNeeded(self):
		"""
			Requests the next rows from the server and feed them to the table.
		"""
		if self._currentCursor:
			filter = self.filter.copy()
			filter["amount"] = self._batchSize
			if self._currentCursor is not None:
				filter["cursor"] = self._currentCursor
			self._currentRequests.append( NetworkService.request(self.modul, "list", filter, successHandler=self.onCompletion, failureHandler=self.showErrorMsg, cacheable=True ) )
			self._currentCursor = None


	def onAttach(self):
		super( ListWidget, self ).onAttach()
		NetworkService.registerChangeListener( self )

	def onDetach(self):
		super( ListWidget, self ).onDetach()
		NetworkService.removeChangeListener( self )

	def onDataChanged(self, modul):
		"""
			Refresh our view if element(s) in this modul have changed
		"""
		if modul and modul!=self.modul:
			return
		self.reloadData( )


	def reloadData(self):
		"""
			Removes all currently displayed data and refetches the first batch from the server.
		"""
		self.table.clear()
		self._currentCursor = None
		self._currentRequests = []
		filter = self.filter.copy()
		filter["amount"] = self._batchSize
		#if self._currentSearchStr:
		#	filter["search"] = self._currentSearchStr
		self.table.setDataProvider( self )
		self._currentRequests.append( NetworkService.request(self.modul, "list", filter, successHandler=self.onCompletion, failureHandler=self.showErrorMsg, cacheable=True ) )


	def setFilter(self, filter):
		"""
			Applies a new filter.
		"""
		self.filter = filter
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
		#self.search.resetLoadingState()
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
		self.table.setHeader( [x["descr"] for x in boneInfoList])
		self.table.setShownFields( fields )
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

class ListWidgetPreview(html5.Div):
	def __init__( self, modul, filter=None, columns=None, isSelector=False, *args, **kwargs ):
		super( ListWidgetPreview, self ).__init__( )
		self.modul = modul

		self.modullist = ListWidget( modul, filter,columns,isSelector,args,kwargs )
		self.modullist.selectionChangedEvent.register( self )

		self.appendChild( self.modullist )
		self.viewwrap = html5.Div()
		self.itemview= html5.Ul()

		self.viewwrap.appendChild(self.itemview)
		self.appendChild(self.viewwrap)

	def onSelectionChanged(self,table,row):
		if self.modullist._structure:
			self.modullist["class"]="halfview"
			for c in self.itemview._children[:]:
				self.itemview.removeChild(c)
			tmpDict = {}
			for key, bone in self.modullist._structure:
				tmpDict[ key ] = bone

			for key, bone in self.modullist._structure:
				self.ali= html5.Li()
				self.ali["class"]=[self.modul,"type_"+bone["type"],"bone_"+key]
				self.adl= html5.Dl()

				self.adt=html5.Dt()
				self.adt.appendChild(html5.TextNode(bone["descr"]))

				self.aadd=html5.Dd()
				delegateFactory = viewDelegateSelector.select( self.modul, key, tmpDict )( self.modul, key, tmpDict )
				self.aadd.appendChild(delegateFactory.render(row[0],key))

				self.adl.appendChild(self.adt)
				self.adl.appendChild(self.aadd)
				self.ali.appendChild(self.adl)

				self.itemview.appendChild(self.ali)
