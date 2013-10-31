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
from widgets import ModulListWidget, TopBarWidget, DataTable
from __pyjamas__ import JS
import json
from network import NetworkService
import handler
import bones
import actions
from priorityqueue import HandlerClassSelector

import pygwt




class CoreWindow(Panel,FocusWidget):
	def __init__(self, *args, **kwargs ):
		self.setElement( DOM.createElement("div") )
		super( CoreWindow, self ).__init__( *args, **kwargs )
		self.topBar = TopBarWidget()
		self.adopt( self.topBar,self.getElement())
		self.workSpace = DOM.createElement("div")
		self.workSpace.setAttribute("class","vi_workspace")
		DOM.appendChild( self.element, self.workSpace )
		self.modulMgr = DOM.createElement("div")
		self.modulMgr.setAttribute("class","vi_wm")
		DOM.appendChild( self.workSpace, self.modulMgr )
		self.modulList = DOM.createElement("nav")
		DOM.setElemAttribute( self.modulList, "class", "vi_manager" )
		DOM.appendChild( self.modulMgr, self.modulList )
		self.modulListUl = DOM.createElement("ul")
		DOM.setElemAttribute(self.modulListUl,"class","modullist")
		DOM.appendChild( self.modulList, self.modulListUl)
		self.viewport = DOM.createElement("div")
		DOM.setElemAttribute(self.viewport,"class","vi_viewer")
		DOM.appendChild(self.workSpace, self.viewport)
		#DOM.appendChild( self.modulMgr, self.modulList )
		#self.modulList = ModulListWidget()
		#self.adopt( self.modulList,self.modulMgr )
		#self.modulList.onAttach()
		self.currentPane = None
		self.panes = []
		NetworkService.request( None, "/admin/config", successHandler=self.onCompletion,
					failureHandler=self.onError, cacheable=True )

	def onCompletion(self, req):
		print("ONLOAD MODULES")
		data = NetworkService.decode(req)
		for modulName, modulInfo in data["modules"].items():
			conf[modulName] = modulInfo
			handlerCls = HandlerClassSelector.select( modulName, modulInfo )
			assert handlerCls is not None, "No handler avaiable for modul %s" % modulName
			handler = handlerCls( modulName, modulInfo )
			self.addPane( handler )



	def onError(self, req, code):
		print("ONERROR")

	def addPane(self, pane, parentPane=None):
		#paneHandle = "pane_%s" % self.paneIdx
		#self.paneIdx += 1
		self.panes.append( pane )
		if parentPane:
			parentPane.addChildPane( pane )
			pane.parent = parentPane
		else:
			DOM.appendChild(self.modulListUl, pane.getElement())
			pane.parent = self
		DOM.appendChild( self.viewport, pane.widgetsDomElm )
		DOM.setStyleAttribute(pane.widgetsDomElm, "display", "none" )
		pane.onAttach()



	def stackPane(self, pane):
		assert self.currentPane is not None, "Cannot stack a pane. There's no current one."
		return( self.addPane( pane, parentPane=self.currentPane ) )

	def focusPane(self, pane):
		print("FOCUS PANE", pane)
		assert pane in self.panes, "Cannot focus unknown pane!"
		if self.currentPane is not None:
			DOM.setStyleAttribute(self.currentPane.widgetsDomElm, "display", "none" )
		self.currentPane = pane
		DOM.setStyleAttribute(self.currentPane.widgetsDomElm, "display", "block" )

	def removePane(self, pane):
		assert pane in self.panes, "Cannot remove unknown pane!"
		self.panes.remove( pane )
		if pane==self.currentPane:
			if self.panes:
				self.focusPane( self.panes[-1])
			else:
				self.currentPane == None
		if pane.parent == self:
			DOM.removeChild( self.modulListUl, pane.getElement() )
		else:
			pane.parent.removeChildPane( pane )
		DOM.removeChild( self.viewport, pane.widgetsDomElm )
		pane.onDetach()

	def addWidget(self, widget, pane ):
		pane.addWidget( widget )

	def stackWidget(self, widget ):
		assert self.currentPane is not None, "Cannot stack a widget while no pane is active"
		self.addWidget( widget, self.currentPane )


	def removeWidget(self, widget ):
		for pane in self.panes:
			if widget in pane.widgets:
				pane.removeWidget( widget )
				return
		raise AssertionError("Tried to remove unknown widget %s" % str( widget ))

if __name__ == '__main__':
	pyjd.setup("public/admin.html")
	conf["mainWindow"] = CoreWindow()
	RootPanel().add( conf["mainWindow"] )
	"""
	t = DataTable()
	conf["mainWindow"].addWidget(t,"test")
	tmp = {"1":"Erstellt am",
	       "2":u"Name",
	       "3":u"Serie",
	       "4":u"Verfügbar in",
	       "5":u"Auffindbar über Produktfinder",
	       "6":u"Einbauort",
	       "7":u"Oberfläche",
	       "8":u"Glass"}
	t.add( tmp )
	tmp = {"1":"12.02.2013 10:27:49",
	       "2":u"Runddusche, 2-Teilig",
	       "3":u"Exklusiv",
	       "4":u"Schweiz, Deutschland, Österreich",
	       "5":u"Ja",
	       "6":u"Raumecke",
	       "7":u"ägäis, bahama-beige, ebony, (schwarz-matt), rot (RAL 3003)",
	       "8":u"klar hell, chinchilla"}
	t.add( tmp )
	for x in range(0,25):
		tmp = {}
		for y in range(0,10):
			tmp[str(y)] = "val"+str(y)
		t.add( tmp )
			#t.add( Label( "%s-%s" % (x,y)),x,y)
	t.setShownFields(["1","2","3","4","5","6","7","8"])
	"""
	#t.setFocus( True )
	#conf["mainWindow"].addWidget(None,"test")
	pyjd.run()