import pyjd # this is dummy in pyjs.
from pyjamas.ui.RootPanel import RootPanel
from pyjamas.ui.Button import Button
from pyjamas.ui.HTML import HTML
from pyjamas.ui.Label import Label
from pyjamas.ui import Event
from pyjamas import Window
from pyjamas.HTTPRequest import HTTPRequest
from pyjamas.ui.FocusWidget import FocusWidget
from pyjamas.ui.Widget import Widget
from pyjamas.ui.Panel import Panel
from pyjamas import DOM
import json
from network import NetworkService
from priorityqueue import viewDelegateSelector
from widgets.table import DataTable
from widgets.actionbar import ActionBar

import pygwt




class ListWidget( Widget ):
	"""
		Provides the interface to list-applications.
		It acts as a dataprovider for a DataTable and binds an actionbar
		to this table.

	"""
	def __init__( self, modul, *args, **kwargs ):
		"""
			@param modul: Name of the modul we shall handle. Must be a list application!
			@type modul: string
		"""
		self.element = DOM.createElement("div")
		super( ListWidget, self ).__init__( self.element )
		self.modul = modul
		#self.setStyleName("vi_viewer")
		self.actionBar = ActionBar( self, modul )
		DOM.appendChild( self.element, self.actionBar.getElement() )
		self.actionBar.onAttach()
		self.table = DataTable()
		#self.table = DOM.createElement("table")
		DOM.appendChild( self.element, self.table.getElement() )
		self.table.onAttach()
		self._currentCursor = None
		self.reloadData()
		self.table.setDataProvider(self)
		#Proxy some events and functions of the original table
		for f in ["selectionChangedEvent","selectionActivatedEvent","cursorMovedEvent","getCurrentSelection"]:
			setattr( self, f, getattr(self.table,f))
		self.actionBar.setActions(["add","edit","delete"])
		#HTTPRequest().asyncGet("/admin/%s/list" % self.modul, self)


	def onNextBatchNeeded(self):
		"""
			Requests the next rows from the server and feed them to the table.
		"""
		print("NEXT BATCH")
		if self._currentCursor:
			NetworkService.request(self.modul, "list", {"orderby":"name","amount":"7","cursor":self._currentCursor}, successHandler=self.onCompletion, cacheable=True )
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
		print("GOT DATA CHANGED EVENT")
		self.table.clear()
		self._currentCursor = None
		self.reloadData( )

	def reloadData(self, modul=None ):
		print("DIOG RELOAD")
		NetworkService.request(self.modul, "list", {"orderby":"name","amount":"7"}, successHandler=self.onCompletion, cacheable=True )

	def onCompletion(self, req):
		"""
			Pass the rows received to the datatable.
			@param req: The network request that succeded.
		"""
		data = NetworkService.decode( req )
		if data["structure"] is None:
			if self.table.getRowCount():
				self.table.setDataProvider(None) #We cant load any more results
			else:
				pass
				#self.element.innerHTML = "<center><strong>Keine Ergebnisse</strong></center>"
			return
		boneList = []
		boneInfoList = []
		tmpDict = {}
		for key, bone in data["structure"]:
			tmpDict[ key ] = bone
		for boneName, boneInfo in data["structure"]:
			delegateFactory = viewDelegateSelector.select( self.modul, boneName, tmpDict )( self.modul, boneName, tmpDict )
			self.table.setCellRender( boneName, delegateFactory )
			if boneInfo["visible"]:
				boneList.append( boneName )
				boneInfoList.append( boneInfo )
				#res += "<td>%s</td>" % boneInfo["descr"]
		for skel in data["skellist"]:
			self.table.add( skel )
		self.table.setShownFields( boneList )
		self.table.setHeader( [x["descr"] for x in boneInfoList])
		if "cursor" in data.keys():
			self._currentCursor = data["cursor"]



	def onError(self, text, code):
		l = Label("FAILED")
		RootPanel().add(l)
		l = Label(code)
		RootPanel().add(l)

	def onTimeout(self, text):
		l = Label("TIMEOUT")
		RootPanel().add(l)
		l = Label(unicode(text))
		RootPanel().add(l)