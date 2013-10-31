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
from priorityqueue import HandlerClassSelector
from config import conf

import pygwt

class ModulListWidget(Widget):
	"""
		Fetches the list of all modules from the server, select the
		best handler for it and display theses handlers in the left
		bar of this application.
	"""

	def __init__(self):
		self.element = DOM.createElement("nav")
		self.setStyleName( "vi_manager")
		super(ModulListWidget,self ).__init__( self.element)

		self.ul = DOM.createElement("ul")
		self.ul.setAttribute("class","modullist")
		DOM.appendChild( self.element, self.ul )
		NetworkService.request( None, "/admin/config", successHandler=self.onCompletion,
					failureHandler=self.onError, cacheable=True )


	def onCompletion(self, req):
		data = NetworkService.decode(req)
		for modulName, modulInfo in data["modules"].items():
			conf[modulName] = modulInfo
			handlerCls = HandlerClassSelector.select( modulName, modulInfo )
			assert handlerCls is not None, "No handler avaiable for modul %s" % modulName
			handler = handlerCls( modulName, modulInfo )
			DOM.appendChild( self.ul, handler.element )
			handler.setParent( self )
			handler.onAttach()
			#DOM.appendChild( self.ul, li )


	def onError(self, req, code):
		self.element.innerHTML = "<strong>Failed to fetch the list of modules from the server</strong>"
		l = Label("FAILED")
		RootPanel().add(l)
		l = Label(code)
		RootPanel().add(l)
