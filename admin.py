#-*- coding: utf-8 -*-

import html5
from config import conf
from widgets import TopBarWidget
from widgets.userlogoutmsg import UserLogoutMsg
from network import NetworkService, DeferredCall
from event import viInitializedEvent, EventDispatcher
from priorityqueue import HandlerClassSelector, initialHashHandler, startupQueue
from log import Log
from pane import GroupPane

# THESE MUST REMAIN AND ARE QUEUED!!
import handler
import bones
import actions
import i18n

class AdminScreen(html5.Div):

	def __init__(self, parent, *args, **kwargs ):
		super(AdminScreen, self).__init__(*args, **kwargs)
		parent.appendChild(self)

		self["id"] = "CoreWindow"
		conf["mainWindow"] = self

		self.logoutEvent = EventDispatcher("logout")
		self.logoutEvent.register(parent)

		self.topBar = TopBarWidget()
		self.appendChild( self.topBar )

		self.workSpace = html5.Div()
		self.workSpace["class"] = "vi_workspace"
		self.appendChild(self.workSpace)

		self.modulMgr = html5.Div()
		self.modulMgr["class"] = "vi_wm"
		self.appendChild(self.modulMgr)

		self.modulList = html5.Nav()
		self.modulList["class"] = "vi_manager"
		self.modulMgr.appendChild(self.modulList)

		self.modulListUl = html5.Ul()
		self.modulListUl["class"] = "modullist"
		self.modulList.appendChild(self.modulListUl)

		self.viewport = html5.Div()
		self.viewport["class"] = "vi_viewer"
		self.workSpace.appendChild(self.viewport)

		self.logWdg = Log()
		self.appendChild(self.logWdg)

		self.currentPane = None
		self.nextPane = None #Which pane gains focus once the deferred call fires
		self.panes = [] # List of known panes. The ordering represents the order in which the user visited them.
		self.config = None
		self.user = None
		self.userLoggedOutMsg = UserLogoutMsg()

		self["class"].append("is_loading")

		startupQueue.setFinalElem(self.startup)

		# Register the error-handling for this iframe
		le = eval("window.top.logError")
		w = eval("window")
		w.onerror = le
		w = eval("window.top")
		w.onerror = le
		self.hide()

	def invoke(self):
		self.show()
		startupQueue.run()

	def startup(self):
		NetworkService.request(None, "/admin/config", successHandler=self.postInit,
								failureHandler=self.onError, cacheable=True)

	def log(self, type, msg ):
		self.logWdg.log( type, msg )

	def postInit(self, req):
		self.config = NetworkService.decode(req)

		def getModulName(argIn):
			try:
				return argIn[1]["name"].lower()
			except:
				return None

		def getModulSortIndex(argIn):
			try:
				return argIn[1]["sortIndex"]
			except:
				return None

		# Modules
		groups = {}
		panes = []
		userAccess = conf["currentUser"].get("access", [])
		predefinedFilterCounter = 1

		if ( "configuration" in self.config.keys()
		     and isinstance( self.config["configuration"], dict )
		     and "modulGroups" in self.config["configuration"].keys()
		     and isinstance( self.config["configuration"]["modulGroups"], list) ):

			for group in self.config["configuration"]["modulGroups"]:
				p = GroupPane( group["name"], iconURL=group["icon"] )

				groups[ group["prefix"] ] = p
				if "sortIndex" in group.keys():
					sortIndex = group["sortIndex"]
				else:
					sortIndex = None

				panes.append( (group["name"], sortIndex, p) )

		# Sorting the 2nd level entries
		sorted_modules = [(x,y) for x,y in self.config["modules"].items()]
		sorted_modules.sort(key=getModulName)
		sorted_modules.sort(key=getModulSortIndex, reverse=True)

		for module, info in sorted_modules:
			if not "root" in userAccess and not any([x.startswith(module) for x in userAccess]):
				#Skip this module, as the user couldn't interact with it anyway
				continue

			conf["modules"][module] = info

			if "views" in conf["modules"][module].keys() and conf["modules"][module]["views"]:
				for v in conf["modules"][module]["views"]: #Work-a-round for PyJS not supporting id()
					v["__id"] = predefinedFilterCounter
					predefinedFilterCounter += 1

			handlerCls = HandlerClassSelector.select(module, info)
			print(module, info)

			assert handlerCls is not None, "No handler available for module '%s'" % module

			isChild = False
			for k in groups.keys():
				if info["name"].startswith(k):
					handler = handlerCls( module, info, groupName=k )
					groups[k].addChildPane( handler )
					isChild = True
					break

			if not isChild:
				handler = handlerCls( module, info )
				if "sortIndex" in info.keys():
					sortIndex = info["sortIndex"]
				else:
					sortIndex = None
				panes.append( ( info["name"], sortIndex, handler ) )

		# Sorting our top level entries
		panes.sort( key=lambda x: x[0] )
		panes.sort( key=lambda x: x[1], reverse=True )

		# Push the panes, ignore group panes with no children (due to right restrictions)
		for k, v, pane in panes:
			# Don't display GroupPanes without children.
			if ( isinstance( pane, GroupPane )
			     and ( not pane.childPanes
			           or all( child[ "style" ].get( "display" ) == "none" for child in pane.childPanes ) ) ):
				continue

			self.addPane( pane )

		# Finalizing!
		viInitializedEvent.fire()
		DeferredCall( self.checkInitialHash )
		self["class"].remove("is_loading")

	def checkInitialHash( self, *args, **kwargs ):
		urlHash = eval("window.top.location.hash")
		if not urlHash:
			return
		if "?" in urlHash:
			hashStr = urlHash[ : urlHash.find("?") ]
			paramsStr = urlHash[ urlHash.find("?")+1: ]
		else:
			hashStr = urlHash
			paramsStr = ""
		hashList = hashStr[1:].split("/")
		hashList = [x for x in hashList if x]
		params = {}
		if paramsStr:
			for pair in paramsStr.split("&"):
				if not "=" in pair:
					continue
				key = pair[ :pair.find("=") ]
				value = pair[ pair.find("=")+1: ]
				if not (key and value):
					continue
				if key in params.keys():
					if not isinstance( params[ key ], list ):
						params[ key ] = [ params[ key ] ]
					params[ key ].append( value )
				else:
					params[ key ] = value
		gen = initialHashHandler.select( hashList, params )
		if gen:
			gen( hashList, params )

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

	def stackPane(self, pane, focus=False):
		assert self.currentPane is not None, "Cannot stack a pane. There's no current one."
		self.addPane( pane, parentPane=self.currentPane )
		if focus and not self.nextPane:
			#We defer the call to focus, as some widgets stack more than one pane at once.
			#If we focus directly, they will stack on each other, instead of the pane that
			#currently has focus
			self.nextPane = pane
			DeferredCall( self.focusNextPane )

	def focusNextPane(self, *args, **kwargs):
		"""
			The deferred call just fired. Focus that pane.
		"""
		if not self.nextPane:
			return

		nextPane = self.nextPane
		self.nextPane = None

		self.focusPane( nextPane )

	def focusPane(self, pane):
		assert pane in self.panes, "Cannot focus unknown pane!"
		#print( pane.descr, self.currentPane.descr if self.currentPane else "(null)" )

		# Click on the same pane?
		if pane == self.currentPane:
			if self.currentPane.collapseable and self.currentPane.childDomElem:
				if self.currentPane.childDomElem["style"]["display"] == "none":
					self.currentPane.childDomElem["style"]["display"] = "block"
				else:
					self.currentPane.childDomElem["style"]["display"] = "none"
			return

		self.panes.remove( pane ) # Move the pane to the end of the list
		self.panes.append( pane )

		# Close current Pane
		if self.currentPane is not None:
			self.currentPane["class"].remove("is_active")
			self.currentPane.widgetsDomElm["style"]["display"] = "none"

		# Focus wanted Pane
		self.topBar.setCurrentModulDescr( pane.descr, pane.iconURL, pane.iconClasses )
		self.currentPane = pane
		self.currentPane.widgetsDomElm["style"]["display"] = "block"

		if self.currentPane.collapseable and self.currentPane.childDomElem:
			self.currentPane.childDomElem["style"]["display"] = "block"

		self.currentPane["class"].append("is_active")

	def removePane(self, pane):
		assert pane in self.panes, "Cannot remove unknown pane!"
		self.panes.remove( pane )
		if pane == self.currentPane:
			if self.panes:
				self.focusPane( self.panes[-1])
			else:
				self.currentPane = None

		if pane == self.nextPane:
			if self.panes:
				self.nextPane = self.panes[-1]
			else:
				self.nextPane = None

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
