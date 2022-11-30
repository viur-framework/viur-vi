# -*- coding: utf-8 -*-
import os, time
from flare import html5, utils, bindApp
from flare.event import EventDispatcher
from .config import conf, updateConf
from .widgets import TopBarWidget
from .widgets.userlogoutmsg import UserLogoutMsg
from flare.network import NetworkService, DeferredCall

from .priorityqueue import HandlerClassSelector, initialHashHandler, startupQueue
from .log import Log
from .pane import Pane, GroupPane
from .screen import Screen

from flare.popup import Popup

from flare.views.helpers import registerViews, generateView, addView, updateDefaultView
from vi.widgets.appnavigation import AppNavigation
from flare.i18n import translate

# BELOW IMPORTS MUST REMAIN AND ARE QUEUED!!
from . import actions
from flare.viur import bones
from flare import i18n
from vi.widgets.list import ListWidget
from vi.widgets.tree import TreeWidget
from vi.widgets.file import FileWidget
from vi.widgets.hierarchy import HierarchyWidget


class AdminScreen(Screen):

	def __init__(self, *args, **kwargs):
		super(AdminScreen, self).__init__(*args, **kwargs)

		self.sinkEvent("onClick")
		self["id"] = "CoreWindow"

		conf["mainWindow"] = self
		_conf = bindApp(self, conf)  # configure Flare Framework
		updateConf(_conf)

		self.topBar = TopBarWidget()
		self.appendChild(self.topBar)

		self.mainFrame = html5.Div()
		self.mainFrame["class"] = "vi-main-frame"
		self.appendChild(self.mainFrame)

		self.moduleMgr = html5.Div()
		self.moduleMgr["class"] = "vi-manager-frame"
		self.mainFrame.appendChild(self.moduleMgr)

		self.moduleViMgr = html5.Div()
		self.moduleViMgr["class"] = "vi-manager"
		self.moduleMgr.appendChild(self.moduleViMgr)

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
		if utils.doesEventHitWidgetOrChildren(event, self.modulePipe) and conf["modulepipe"]:
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

	def refresh(self):
		NetworkService.request(None, "/vi/config",
									   successHandler=self.refreshConfig,
									   failureHandler=self.getCurrentUserFailure)

	def refreshConfig(self,req):
		conf["mainConfig"] = NetworkService.decode(req)
		self.invoke()

	def startup(self):
		config = conf["mainConfig"]
		assert config

		if not conf["currentUser"]:
			self.getCurrentUser()
			return

		conf["server"] = config.get("configuration", {})

		if name := conf["server"].get("vi.name"):
			conf["vi.name"] = str(name)

		if customcss := conf["server"].get("vi.customcss"):
			html5.Head().appendChild(
				# language=html
				f"""<link rel="stylesheet" href="{customcss}">"""
			)

		self.userLoggedOutMsg = UserLogoutMsg()
		self.topBar.invoke()

		self.initializeViews()
		self.initializeConfig()
		DeferredCall(self.checkInitialHash)
		self.unlock()

	def initializeViews(self):
		root = os.path.dirname(__file__)  # path to root package
		if "/vi.zip" in root:
			registerViews("/vi.zip/vi", "views")
		else:
			registerViews(root, "views")
		# load default View
		updateDefaultView("overview")
		conf["views_state"].updateState("activeView", "overview")
		from vi import s
		import time

		print("%.5f Sek - ready to View" % (time.time() - s))

	def initializeConfig(self):
		# print("------------------------------")
		# print(conf["mainConfig"]["configuration"])
		groups = conf["mainConfig"]["configuration"].get("moduleGroups", {})
		modules = conf["mainConfig"]["modules"]

		assert isinstance(groups, dict), "moduleGroups has to be a dictionary!"
		mergedItems = []
		for k, v in groups.items():
			v.update({"prefix": k})
			mergedItems.append(v)

		for key, m in modules.items():
			# convert dict of dicts to list of dicts
			m.update({"moduleName": key})

			# add missing sortIndexes
			if "sortIndex" not in m and "name" in m:  # no sortidx but name
				m.update({"sortIndex": ord(m["name"][0].lower()) - 97})
			elif "sortIndex" not in m and "name" not in m:  # no sortidx, no name
				m.update({"sortIndex": 0})

			if "moduleGroup" in m and m["moduleGroup"]:
				group = m["moduleGroup"]

				# stack modules in groups
				getGroup = next((item for item in mergedItems if "prefix" in item and item["prefix"] == group), None)

				if not getGroup:  # corrupt group definition, add as normal module
					mergedItems.append(m)
					continue

				if "subItem" not in getGroup:
					getGroup.update({"subItem": [m]})
				else:
					getGroup["subItem"].append(m)
			else:
				# add normal modules without groups
				mergedItems.append(m)

		# sort firstLayer
		mergedItems = sorted(mergedItems, key=lambda i: i.get("sortIndex", 0))

		# all will be add to this Widget
		adminGroupWidget = self.navWrapper.addNavigationBlock("Administration")
		self.appendNavList(mergedItems, adminGroupWidget)

	def appendNavList(self, NavList, target, parentInfo=()):
		for idx, item in enumerate(NavList):
			viewInst = None
			if "moduleName" in item:  # its a module
				# update conf
				conf["modules"][item["moduleName"]] = item

				# get handler view
				handlerCls = HandlerClassSelector.select(item["moduleName"], item)
				# generate a parameterized view
				instancename = item["moduleName"] + item["handler"]
				viewInst = generateView(handlerCls, item["moduleName"], item["handler"], data=item)

			elif parentInfo:

				# this is a view, cause parentInfo is only provided by views

				# Extend some inherited attributes from moduleInfo
				for inherit in ["+name", "+columns", "+filter", "+context", "+actions", "+handler"]:
					if inherit in item:
						inherit = inherit[1:]

						if inherit in parentInfo:
							if isinstance(parentInfo[inherit], list):
								assert isinstance(item["+" + inherit], list)

								if inherit not in item:
									item[inherit] = parentInfo[inherit][:]

								item[inherit].extend(item["+" + inherit])
							elif isinstance(parentInfo[inherit], dict):
								assert isinstance(item["+" + inherit], dict)

								if inherit not in item:
									item[inherit] = parentInfo[inherit]

								item[inherit].update(item["+" + inherit])

							else:
								item[inherit] = parentInfo[inherit] + item["+" + inherit]

						else:
							item[inherit] = item["+" + inherit]

						del item["+" + inherit]

				# collect parentdata
				for inherit in ["moduleName", "icon", "columns", "filter", "context", "handler"]:
					if inherit not in item and inherit in parentInfo:
						item[inherit] = parentInfo[inherit]

				# get handler view
				handlerCls = HandlerClassSelector.select(item["moduleName"], item)

				# generate a parameterized view
				instancename = "%s___%s" % (item["moduleName"] + item["handler"], str(time.time()).replace(".", "_"))

				# add unique filterID
				item["filterID"] = idx + 1

				# create new viewInstance
				viewInst = generateView(handlerCls, item["moduleName"], item["handler"], data=item, name=instancename)
			else:
				# moduleGroup
				instancename = None

			if instancename:
				# register this new view
				conf["views_registered"].update({instancename: viewInst})

			# only generate navpoints if module is visible
			if ("display" in item and item["display"] == "hidden"):
				continue

			# skip Empty groups
			if "prefix" in item and "subItem" not in item:
				continue

			# get  viewName
			if "display" in item and item["display"] == "group":
				viewInstName = None
			else:
				viewInstName = viewInst.name if viewInst else "notfound"

			# get open State
			if "display" in item and item["display"] == "open":
				isOpen = True
			else:
				isOpen = False

			# visible module
			currentModuleWidget = self.navWrapper.addNavigationPoint(
				item.get("name", "missing Name"),
				item.get("icon", None),
				viewInstName,
				target,
				opened=isOpen
			)

			# sort and append Items modules in a Group
			if "subItem" in item and item["subItem"]:
				subItems = sorted(item["subItem"], key=lambda i: i.get("sortIndex", 0))
				self.appendNavList(subItems, currentModuleWidget)

			# sort and append views of a Module
			if "views" in item and item["views"]:
				viewItems = sorted(item["views"], key=lambda i: i.get("sortIndex", 0))
				self.appendNavList(viewItems, currentModuleWidget, item)

	def openView(self, name, icon, viewName, moduleName, actionName, data, focusView=True, append=False,
				 target="mainNav"):
		if target == "mainNav":
			self.openNewMainView(name, icon, viewName, moduleName, actionName, data, focusView, append)
		elif target == "popup":
			self.openNewPopup(name, icon, viewName, moduleName, actionName, data, focusView, append)
		else:
			print("No valid target: %s" % target)

	def openNewMainView(self, name, icon, viewName, moduleName, actionName, data, focusView=True, append=False):
		# generate a parameterized view
		print("actionName %r" % actionName)
		view = conf["views_registered"].get(viewName, "notfound").__class__
		instancename = "%s___%s" % (viewName, str(time.time()).replace(".", "_"))
		viewInst = generateView(view, moduleName, actionName, data=data, name=instancename)
		conf["views_registered"].update({instancename: viewInst})

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
			conf["views_state"].updateState("activeView", instancename)

	def openNewPopup(self, name, icon, viewName, moduleName, actionName, data, focusView=True, append=False):
		view = conf["views_registered"].get(viewName, "notfound").__class__
		instancename = "%s___%s" % (viewName, str(time.time()).replace(".", "_"))
		viewInst = generateView(view, moduleName, actionName, data=data, name=instancename)

		mainWidget = viewInst.widgets["viewport"](viewInst)  # todo better solution is needed

		self.stackWidget(mainWidget, title=name, icon=icon)

	def log(self, type, msg, icon=None, modul=None, action=None, key=None, data=None):
		msg = self.logWdg.log(type, msg, icon, modul, action, key, data)
		return msg

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

		print(path)
		if len(path) >= 2 and path[1] == "list":
			viewname = "".join(path)
			conf["views_state"].updateState("activeView", viewname)
			return
		elif len(path) >= 2 and path[1] in ["edit", "add"]:
			data = {"context": None}  # fixme
			if len(path) == 2:
				handlertype = "singletonhandler"
			elif path[1] == "edit":
				handlertype = "edithandler"
				if len(path) > 3:
					data.update({"group": path[2]})
					data = {"key": path[3], "context": None}  # fixme
				else:
					data = {"key": path[2], "context": None}  # fixme
			else:
				if len(path) >= 3:
					data.update({"group": path[2]})
				handlertype = "edithandler"

			conf["views_state"].updateState("activeView", path[0] + "list")
			conf["mainWindow"].openView(
				translate(path[1]),  # AnzeigeName
				"icon-" + path[1],  # Icon
				handlertype,  # viewName
				path[0],  # Modulename
				path[1],  # Action
				data=data
			)

	def stackWidget(self, widget, title="", icon=None):
		'''
			We dont stack widgets anymore.
			We use now Popups.


		'''
		widgetPopup = Popup(title=title, icon=icon)
		widgetPopup["style"]["width"] = "auto"
		widgetPopup["style"]["max-width"] = "90%"
		widgetPopup["style"]["height"] = "90%"

		widget.parentPopup = widgetPopup
		widgetPopup.popupBody.appendChild(widget)

	def removeWidget(self, widget):
		if "parentPopup" in dir(widget):
			widget.parentPopup.close()

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
