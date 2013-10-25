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
		self.modulMgr.setAttribute("class","vi_manager")
		DOM.appendChild( self.element, self.modulMgr )
		self.modulList = ModulListWidget()
		self.adopt( self.modulList,self.modulMgr )
		self.modulList.onAttach()
		self.currentPane = None
		self.panes = {}

	def addWidget(self, widget, pane ):
		if not pane in self.panes.keys():
			self.panes[ pane ] = []
			paneDiv = DOM.createElement("div")
			DOM.setElemAttribute(paneDiv,"class","vi_viewer")
			paneDiv.id = "core_window_"+pane
			#paneDiv.id = "core_window_"+pane
			DOM.appendChild( self.workSpace, paneDiv )
			#DOM.setAttribute( paneDiv, "id", "core_window_"+pane )
		if self.currentPane is not None:
			oldPaneElem = DOM.getElementById( "core_window_"+self.currentPane )
			DOM.setStyleAttribute(oldPaneElem, "display", "none" )
			#self.disown( self.current )
			#self.current.onDetach()
			#self.current = None
		paneElem = DOM.getElementById( "core_window_"+pane )
		assert paneElem, "The pane DIV seems missing!"
		self.currentPane = pane
		self.panes[ pane ].append( widget )
		DOM.setStyleAttribute(paneElem, "display", "block" )
		DOM.appendChild( paneElem, widget.getElement() )
		widget.setParent( self )
		widget.onAttach()

	def removeWidget(self, widget ):
		for paneName, widgetList in self.panes.items():
			if widget in widgetList:
				widget.onDetach()
				DOM.removeChild( DOM.getElementById("core_window_"+paneName), widget.getElement() )
				widgetList.remove( widget )
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