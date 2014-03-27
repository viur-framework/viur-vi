import pyjd
import html5
from config import conf
from widgets import TopBarWidget
from widgets.userlogoutmsg import UserLogoutMsg
import json
from network import NetworkService, DeferredCall
import handler
import bones
import actions
from event import viInitializedEvent
from priorityqueue import HandlerClassSelector, initialHashHandler, startupQueue
from log import Log
from pane import Pane, GroupPane
from i18n import translate

try:
	import vi_plugins
except ImportError:
	pass


class CoreWindow( html5.Div ):


	def __init__(self, *args, **kwargs ):
		super( CoreWindow, self ).__init__( *args, **kwargs )
		self["id"]="CoreWindow"
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
		self.logWdg = Log()
		self.appendChild( self.logWdg )
		#DOM.appendChild( self.modulMgr, self.modulList )
		#self.modulList = ModulListWidget()
		#self.adopt( self.modulList,self.modulMgr )
		#self.modulList.onAttach()
		self.currentPane = None
		self.panes = [] # List of known panes. The ordering represents the order in which the user visited them.
		self.config = None
		self.user = None
		self.userLoggedOutMsg=UserLogoutMsg()
		versionDiv = html5.Div()
		versionDiv["class"].append("versiondiv")
		#Try loading the version number
		try:
			from version import builddate,revision
			revspan = html5.Span()
			revspan.appendChild( html5.TextNode( translate("Revision: {rev}",rev=revision )))
			revspan["class"].append("revisionspan")
			datespan = html5.Span()
			datespan.appendChild( html5.TextNode( translate("Build Date: {date}",date=builddate) ))
			datespan["class"].append("datespan")
			versionDiv.appendChild( datespan )
			versionDiv.appendChild( revspan )
		except:
			versionDiv.appendChild( html5.TextNode( translate("unknown build") ) )
		#self.appendChild( versionDiv )
		startupQueue.setFinalElem( self.startup )
		self.sinkEvent('onUserTryedToLogin')

	def onUserTryedToLogin(self,event):
		self.userLoggedOutMsg.testUserAvaiable()

	def startup(self):
		NetworkService.request( None, "/admin/config", successHandler=self.onConfigAvaiable,
					failureHandler=self.onError, cacheable=True )
		NetworkService.request( None, "/admin/user/view/self", successHandler=self.onUserAvaiable,
					failureHandler=self.userLoggedOutMsg.onUserTestFail, cacheable=True )

	def log(self, type, msg ):
		self.logWdg.log( type, msg )

	def onConfigAvaiable(self, req):
		data = NetworkService.decode(req)
		self.config = data
		if self.user is not None:
			self.postInit()
	
	
	def onUserAvaiable(self, req):
		data = NetworkService.decode(req)
		conf["currentUser"] = data["values"]
		self.user = data
		if self.config is not None:
			self.postInit()


	def postInit(self):
		groups = {}
		panes = []
		userAccess = self.user["values"]["access"]
		if "configuration" in self.config.keys() and isinstance( self.config["configuration"], dict) \
			and "modulGroups" in self.config["configuration"].keys() and isinstance( self.config["configuration"]["modulGroups"], list):
			for group in self.config["configuration"]["modulGroups"]:
				p = GroupPane(group["name"],iconURL=group["icon"])
				groups[ group["prefix"] ] = p
				panes.append( (group["name"], p) )
		for modulName, modulInfo in self.config["modules"].items():
			if not "root" in userAccess and not any([x.startswith(modulName) for x in userAccess]):
				#Skip this modul, as the user couldn't interact with it anyway
				continue
			conf["modules"][modulName] = modulInfo
			handlerCls = HandlerClassSelector.select( modulName, modulInfo )
			assert handlerCls is not None, "No handler available for modul %s" % modulName
			handler = handlerCls( modulName, modulInfo )
			isChild = False
			for k in groups.keys():
				if modulInfo["name"].startswith(k):
					groups[k].addChildPane( handler )
					isChild = True
					break
			if not isChild:
				panes.append( ( modulInfo["name"], handler ) )
		panes.sort( key=lambda x: x[0] )
		for k, pane in panes:
			self.addPane( pane )
		viInitializedEvent.fire()
		DeferredCall( self.checkInitialHash )


	def checkInitialHash( self, *args, **kwargs ):
		urlHash = eval("window.top.location.hash")
		print("-------")
		print( urlHash )
		if not urlHash:
			return
		urlHash = urlHash[1:].split("/")
		urlHash = [x for x in urlHash if x]
		gen = initialHashHandler.select( urlHash )
		if gen:
			gen( urlHash )


	def onError(self, req, code):
		print("ONERROR")


	def _registerChildPanes(self, pane ):
		for childPane in pane.childPanes:
			self.panes.append(childPane)
			self.viewport.appendChild(childPane.widgetsDomElm)
			childPane.widgetsDomElm["style"]["display"] = "none"
			self._registerChildPanes(childPane)

	def addPane(self, pane, parentPane=None):
		#paneHandle = "pane_%s" % self.paneIdx
		#self.paneIdx += 1
		if len(pane.childPanes)>0:
			self._registerChildPanes( pane )
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
			self.currentPane["class"].remove("is_active")
		self.topBar.setCurrentModulDescr( pane.descr, pane.iconURL, pane.iconClasses )
		self.currentPane = pane
		self.currentPane.widgetsDomElm["style"]["display"] = "block"
		self.currentPane["class"].append("is_active")

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
			if pane.containsWidget( widget ):
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
	startupQueue.run()
	pyjd.run()

