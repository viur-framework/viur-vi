# -*- coding: utf-8 -*-
import os, time
from flare import html5,utils,bindApp
from flare.event import EventDispatcher
from .config import conf
from .widgets import TopBarWidget
from .widgets.userlogoutmsg import UserLogoutMsg
from flare.network import NetworkService, DeferredCall

from .priorityqueue import HandlerClassSelector, initialHashHandler, startupQueue
from .log import Log
from .pane import Pane, GroupPane
from .screen import Screen

from flare.views.helpers import registerViews, generateView, addView,updateDefaultView
from vi.widgets.appnavigation import AppNavigation

# BELOW IMPORTS MUST REMAIN AND ARE QUEUED!!
from . import actions
from flare.forms import bones
from . import i18n

class AdminScreen(Screen):

	def __init__(self, *args, **kwargs):
		super(AdminScreen, self).__init__(*args, **kwargs)

		self.sinkEvent("onClick")
		self["id"] = "CoreWindow"
		conf["mainWindow"] = self
		bindApp(self,{"basePathSvgs":"/vi/s/public/svgs"}) #configure Flare Framework

		self.topBar = TopBarWidget()
		self.appendChild(self.topBar)

		self.mainFrame = html5.Div()
		self.mainFrame["class"] = "vi-main-frame"
		self.appendChild(self.mainFrame)


		self.moduleMgr = html5.Div()
		self.moduleMgr["class"] = "vi-manager-frame"
		self.mainFrame.appendChild(self.moduleMgr)

		self.moduleViMgr = html5.Div()
		self.moduleViMgr[ "class" ] = "vi-manager"
		self.moduleMgr.appendChild( self.moduleViMgr )

		self.navWrapper = AppNavigation()
		self.moduleViMgr.appendChild(self.navWrapper)

		self.modulePipe = html5.Div()
		self.modulePipe.addClass("vi-modulepipe")
		self.moduleMgr.appendChild(self.modulePipe)

		self.viewport = html5.Div()
		self.viewport["class"] = "vi-viewer-frame"
		self.mainFrame.appendChild(self.viewport)

		self.logWdg = None


	def onClick(self, event):
		if utils.doesEventHitWidgetOrChildren(event, self.modulePipe):
			conf["mainWindow"].switchFullscreen(not conf["mainWindow"].isFullscreen())

	def reset(self):
		self.navWrapper.removeAllChildren()
		self.viewport.removeAllChildren()
		if self.logWdg:
			self.logWdg.reset()

	def invoke(self):
		self.show()
		self.lock()

		self.reset()

		# Run queue
		startupQueue.setFinalElem(self.startup)
		startupQueue.run()

	def getCurrentUser(self):
		NetworkService.request("user", "view/self",
							   successHandler=self.getCurrentUserSuccess,
							   failureHandler=self.getCurrentUserFailure)

	def getCurrentUserSuccess(self, req):
		answ = NetworkService.decode(req)
		conf["currentUser"] = answ["values"]
		self.startup()

	def getCurrentUserFailure(self, req, code):
		conf["theApp"].login()

	def startup(self):
		config = conf["mainConfig"]
		assert config

		if not conf["currentUser"]:
			self.getCurrentUser()
			return

		conf["server"] = config.get("configuration", {})

		if "vi.name" in conf["server"]:
			conf["vi.name"] = str(conf["server"]["vi.name"])

		self.userLoggedOutMsg = UserLogoutMsg()
		self.topBar.invoke()

		self.initializeViews()
		#self.initializeAppNavigation()
		self.initializeConfig()
		self.unlock()
		print(conf)

	def initializeViews( self ):
		root = os.path.dirname(__file__) #path to root package
		registerViews(os.path.join(root,"views"))

		#load default View
		updateDefaultView("overview")
		conf["views_state"].updateState("activeView","overview")
		from vi import s
		import time

		print( "%.5f Sek - ready to View" % (time.time()-s) )

	def initializeAppNavigation( self ):

		#navpoint = self.navWrapper.addNavigationPoint("Test1","icon-users","notfound",block)
		#subpoint1  = self.navWrapper.addNavigationPoint("Test SuB","icon-users","notfound",navpoint)
		#subpoint2 = self.navWrapper.addNavigationPoint("Test SuBSub","icon-users","notfound",subpoint1)
		#subpoint3 = self.navWrapper.addNavigationPoint("Test SuBSubSub","icon-users","notfound",subpoint2)

		#navpoint2 = self.navWrapper.addNavigationPoint( "Test2", "icon-files", "overview", block )

		#for i in range(2,200):
		#	self.navWrapper.addNavigationPoint("Test%s"%i,"icon-file-system","overview",block)

		from vi import s
		import time

		print( "%.5f Sek - ready to Navigate" % (time.time() - s) )

	def initializeConfig( self ):
		#print("------------------------------")
		#print(conf["mainConfig"]["configuration"])
		groups = conf["mainConfig"]["configuration"]["moduleGroups"]
		modules = conf["mainConfig"]["modules"]

		mergedItems = groups
		for key, m in modules.items():
			#convert dict of dicts to list of dicts
			m.update({"moduleName":key})

			#add missing sortIndexes
			if "sortIndex" not in m and "name" in m: #no sortidx but name
				m.update( { "sortIndex": ord(m["name"][0].lower())-97 } )
			elif "sortIndex" not in m and "name" not in m: #no sortidx, no name
				m.update( { "sortIndex": 0} )

			if ": " in m["name"]:
				# find modules that belong to groups

				#maybe a groupprefix
				group = m["name"].split(": ")[0]+": "

				#stack modules in groups
				getGroup = next((item for item in mergedItems if item["prefix"]==group),None)
				m["name"] = m["name"].replace(group,"")
				if "subItem" not in getGroup:
					getGroup.update({"subItem":[m]})
				else:
					getGroup["subItem"].append(m)
			else:
				#add normal modules without groups
				mergedItems.append(m)

		#sort firstLayer
		mergedItems = sorted(mergedItems,key = lambda i:i["sortIndex"])

		#all will be add to this Widget
		adminGroupWidget = self.navWrapper.addNavigationBlock( "Administration" )
		self.appendNavList( mergedItems, adminGroupWidget )

	def appendNavList( self,NavList,target ):
		for item in NavList:
			viewInst = None
			if "moduleName" in item: # its a module
				#update conf
				conf[ "modules" ][ item[ "moduleName" ] ] = item

				#get handler view
				handlerCls = HandlerClassSelector.select( item[ "moduleName" ], item )
				#generate a parameterized view
				viewInst = generateView(handlerCls,item["moduleName"],item["handler"],data=item)

			#only generate navpoints if module is visible
			if "hideInMainBar" not in item  or ("hideInMainBar" in item and not item[ "hideInMainBar" ]):

				#skip Empty groups
				if "prefix" in item and "subItem" not in item:
					continue

				#visible module
				currentModuleWidget = self.navWrapper.addNavigationPoint(
					item.get("name","missing Name"),
					item.get("icon",None),
					viewInst.name if viewInst else "notfound",
					target
				)

				# sort and append Items modules in a Group
				if "subItem" in item and item[ "subItem" ]:
					subItems = sorted( item[ "subItem" ], key = lambda i: i[ "sortIndex" ] )
					self.appendNavList( subItems, currentModuleWidget )

				#sort and append views of a Module
				if "views" in item and item[ "views" ]:
					viewItems = sorted( item[ "views" ], key = lambda i: i[ "sortIndex" ] )
					self.appendNavList( viewItems, currentModuleWidget )


	def openNewMainView( self,name,icon,viewName,moduleName,actionName,data,focusView=True,append=False ):
		# generate a parameterized view
		view = conf["views_registered"].get(viewName,"notfound").__class__
		instancename = "%s___%s" % (viewName, str( time.time() ).replace( ".", "_" ))
		viewInst = generateView( view, moduleName, actionName, data = data,name=instancename )
		conf["views_registered"].update({instancename:viewInst})

		currentActivNavPoint = self.navWrapper.state.getState("activeNavigation")
		if append:
			self.navWrapper.addNavigationPoint(
				name,
				icon,
				viewInst.name if viewInst else "notfound",
				None,
				True
			)
		else:
			self.navWrapper.addNavigationPointAfter(
				name,
				icon,
				viewInst.name if viewInst else "notfound",
				currentActivNavPoint,
				True
			)

		if focusView:
			conf[ "views_state" ].updateState( "activeView", instancename )


	def log(self, type, msg, icon=None,modul=None,action=None,key=None,data=None):
		self.logWdg.log(type, msg, icon,modul,action,key,data)

	def checkInitialHash(self, *args, **kwargs):
		urlHash = html5.window.location.hash
		if not urlHash:
			return

		if "?" in urlHash:
			hashStr = urlHash[1:urlHash.find("?")]
			paramsStr = urlHash[urlHash.find("?") + 1:]
		else:
			hashStr = urlHash[1:]
			paramsStr = ""

		self.execCall(hashStr, paramsStr)

	def execCall(self, path, params=None):
		"""
		Performs an execution call.

		:param path: Path to the module and action
		:param params: Parameters passed to the module
		"""
		path = [x for x in path.split("/") if x]

		param = {}

		if params:
			if isinstance(params, dict):
				param = params
			else:
				for pair in params.split("&"):
					if not "=" in pair:
						continue

					key = pair[:pair.find("=")]
					value = pair[pair.find("=") + 1:]

					if not (key and value):
						continue

					if key in param.keys():
						if not isinstance(param[key], list):
							param[key] = [params[key]]

						param[key].append(value)
					else:
						param[key] = value

		print("execCall", path, param)

		gen = initialHashHandler.select(path, param)
		if gen:
			gen(path, param)


	def stackWidget( self, widget,disableOtherWidgets=True):
		print("TODO")

	def switchFullscreen(self, fullscreen=True):
		if fullscreen:
			self.moduleMgr.addClass("is-collapsed")
			self.viewport.addClass("is-fullscreen")
		else:
			self.moduleMgr.removeClass("is-collapsed")
			self.viewport.removeClass("is-fullscreen")

	def isFullscreen(self):
		return "is-fullscreen" in self.viewport["class"]

	def onError(self, req, code):
		print("ONERROR")

viInitializedEvent = EventDispatcher("viInitialized")
