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
from widgets.table import DataTable

import pygwt




class ListWidget( Widget ):
	def __init__( self, modul, *args, **kwargs ):
		self.element = DOM.createElement("div")
		super( ListWidget, self ).__init__( self.element )
		self.modul = modul
		#self.setStyleName("vi_viewer")
		self.table = DataTable()
		#self.table = DOM.createElement("table")
		DOM.appendChild( self.element, self.table.getElement() )
		self.table.onAttach()
		self._currentCursor = None
		self.reloadData()
		self.table.setDataProvider(self)
		#HTTPRequest().asyncGet("/admin/%s/list" % self.modul, self)


	def onNextBatchNeeded(self):
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
		self.reloadData( modul )

	def reloadData(self, modul=None ):
		print("DIOG RELOAD")
		if modul and modul!=self.modul:
			return
		NetworkService.request(self.modul, "list", {"orderby":"name","amount":"7"}, successHandler=self.onCompletion, cacheable=True )

	def onCompletion(self, req):
		print("SUCCHESS ")
		data = NetworkService.decode( req )
		if data["structure"] is None:
			if self.table.getRowCount():
				self.table.setDataProvider(None) #We cant load any more results
			else:
				self.element.innerHTML = "<center><strong>Keine Ergebnisse</strong></center>"
			return
		boneList = []
		boneInfoList = []
		for boneName, boneInfo in data["structure"]:
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