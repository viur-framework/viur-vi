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
from config import conf
from widgets import ModulListWidget, TopBarWidget
from __pyjamas__ import JS
import json
from network import NetworkService
from priorityqueue import HandlerClassSelector
from widgets import ListWidget
from config import conf
import pygwt

class ListHandler( FocusWidget ):
	def __init__(self, modulName, modulInfo, *args, **kwargs):
		self.element = DOM.createElement("li")
		self.modulName = modulName
		self.modulInfo = modulInfo
		super( ListHandler, self ).__init__( self.element, *args, **kwargs )
		self.addClickListener( self.onClick )
		self.sinkEvents(Event.ONCLICK | Event.MOUSEEVENTS)
		self.element.innerHTML = "<a href=\"#\"><h3>%s</h3></a>" % modulName
		self.wdg = None


	@staticmethod
	def canHandle( modulName, modulInfo ):
		return( True )

	def onClick(self, *args, **kwargs ):
		if self.modulName == "news":
			#NetworkService.notifyChange( "organisation" )
			from widgets import EditWidget
			conf["mainWindow"].addWidget( EditWidget( "organisation", EditWidget.appList ), "edit" )
		else:
			if not self.wdg:
				self.wdg = ListWidget(self.modulName )
			conf["mainWindow"].addWidget( self.wdg, self.modulName )
		print("ON1CL1ICK", self.modulName)
		print( args )
		print( kwargs )


HandlerClassSelector.insert( 1, ListHandler.canHandle, ListHandler )
