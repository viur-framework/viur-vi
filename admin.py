import pyjd
import html5
from config import conf
from widgets import TopBarWidget
import json
from network import NetworkService
import handler
import bones
import actions
from priorityqueue import HandlerClassSelector



class CoreWindow( html5.Div ):
	def __init__(self, *args, **kwargs ):
		super( CoreWindow, self ).__init__( *args, **kwargs )
		self.topBar = TopBarWidget()
		self.appendChild( self.topBar )
		self.workSpace = html5.Div()
		self.workSpace["class"] = "vi_workspace"
		self.appendChild( self.workSpace )
		self.modulMgr = html5.Div()
		self.modulMgr["class"] = "vi_wm"
		self.appendChild( self.modulMgr )
		self.modulList = html5.Nav()
		self.modulList["class"] = "vi_manager"
		self.modulMgr.appendChild( self.modulList )
		self.modulListUl = html5.Ul()
		self.modulListUl["class"] = "modullist"
		self.modulList.appendChild( self.modulListUl )
		self.viewport = html5.Div()
		self.viewport["class"] = "vi_viewer"
		self.workSpace.appendChild( self.viewport)
		#DOM.appendChild( self.modulMgr, self.modulList )
		#self.modulList = ModulListWidget()
		#self.adopt( self.modulList,self.modulMgr )
		#self.modulList.onAttach()
		self.currentPane = None
		self.panes = [] # List of known panes. The ordering represents the order in which the user visited them.
		NetworkService.request( None, "/admin/config", successHandler=self.onCompletion,
					failureHandler=self.onError, cacheable=True )

	def onCompletion(self, req):
		data = NetworkService.decode(req)
		tmpList = [(k,v) for (k,v) in data["modules"].items()]
		tmpList.sort( key=lambda x:x[1]["name"].lower())
		for modulName, modulInfo in tmpList:# data["modules"].items():
			conf["modules"][modulName] = modulInfo
			handlerCls = HandlerClassSelector.select( modulName, modulInfo )
			assert handlerCls is not None, "No handler available for modul %s" % modulName
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
			self.modulListUl.appendChild( pane )
		self.viewport.appendChild(pane.widgetsDomElm)
		pane.widgetsDomElm["style"]["display"] = "none"
		#DOM.setStyleAttribute(pane.widgetsDomElm, "display", "none" )



	def stackPane(self, pane):
		assert self.currentPane is not None, "Cannot stack a pane. There's no current one."
		return( self.addPane( pane, parentPane=self.currentPane ) )

	def focusPane(self, pane):
		assert pane in self.panes, "Cannot focus unknown pane!"
		self.panes.remove( pane ) # Move the pane to the end of the list
		self.panes.append( pane )
		if self.currentPane is not None:
			self.currentPane.widgetsDomElm["style"]["display"] = "none"
		self.currentPane = pane
		self.currentPane.widgetsDomElm["style"]["display"] = "block"

	def removePane(self, pane):
		assert pane in self.panes, "Cannot remove unknown pane!"
		self.panes.remove( pane )
		if pane==self.currentPane:
			if self.panes:
				self.focusPane( self.panes[-1])
			else:
				self.currentPane == None
		if pane.parent == self:
			self.modulListUl.removeChild( pane )
		else:
			pane.parent.removeChildPane( pane )
		self.viewport.removeChild( pane.widgetsDomElm )

	def addWidget(self, widget, pane ):
		pane.addWidget( widget )

	def stackWidget(self, widget ):
		assert self.currentPane is not None, "Cannot stack a widget while no pane is active"
		self.addWidget( widget, self.currentPane )


	def removeWidget(self, widget ):
		for pane in self.panes:
			if widget in pane.widgetsDomElm._children:
				pane.removeWidget( widget )
				return
		raise AssertionError("Tried to remove unknown widget %s" % str( widget ))

if __name__ == '__main__':
	pyjd.setup("public/admin.html")
	conf["mainWindow"] = CoreWindow()
	html5.Body().appendChild( conf["mainWindow"] )
	#RootPanel().add( conf["mainWindow"] )
	#t.setFocus( True )
	#conf["mainWindow"].addWidget(None,"test")
	pyjd.run()