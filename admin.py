# -*- coding: utf-8 -*-
import os
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

from flare.views.helpers import registerViews
from vi.widgets.appnavigation import AppNavigation

# BELOW IMPORTS MUST REMAIN AND ARE QUEUED!!
from . import handler, bones, actions
from . import i18n

class AdminScreen(Screen):

	def __init__(self, *args, **kwargs):
		super(AdminScreen, self).__init__(*args, **kwargs)

		self.sinkEvent("onClick")
		self["id"] = "CoreWindow"
		conf["mainWindow"] = self
		bindApp(self)

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
		self.initializeAppNavigation()
		self.unlock()

	def initializeViews( self ):
		root = os.path.dirname(__file__) #path to root package
		registerViews(os.path.join(root,"views"))

		#load default View
		conf[ "views_default" ] = "overview"
		conf["views_state"].updateState("activeView", conf["views_default"])
		from vi import s
		import time

		print( "%.5f Sek - ready to View" % (time.time()-s) )

	def initializeAppNavigation( self ):
		block = self.navWrapper.addNavigationBlock("Administration")
		self.navWrapper.addNavigationPoint("Test1","icon-users","notfound",block)

		for i in range(2,200):
			self.navWrapper.addNavigationPoint("Test%s"%i,"icon-file-system","overview",block)

		from vi import s
		import time

		print( "%.5f Sek - ready to Navigate" % (time.time() - s) )

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
