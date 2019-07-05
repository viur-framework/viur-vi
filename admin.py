# -*- coding: utf-8 -*-
import html5

from config import conf
from widgets import TopBarWidget
from widgets.userlogoutmsg import UserLogoutMsg
from network import NetworkService, DeferredCall
from event import viInitializedEvent
from priorityqueue import HandlerClassSelector, initialHashHandler, startupQueue
from log import Log
from pane import Pane, GroupPane
from screen import Screen

# BELOW IMPORTS MUST REMAIN AND ARE QUEUED!!
import handler
import bones
import actions
import i18n


class AdminScreen(Screen):

	def __init__(self, *args, **kwargs):
		super(AdminScreen, self).__init__(*args, **kwargs)

		self.sinkEvent("onClick")
		self["id"] = "CoreWindow"
		conf["mainWindow"] = self

		self.topBar = TopBarWidget()
		self.appendChild(self.topBar)

		self.mainFrame = html5.Div()
		self.mainFrame["class"] = "vi-main-frame"
		self.appendChild(self.mainFrame)


		self.moduleMgr = html5.Div()
		self.moduleMgr["class"] = "vi-manager-frame"
		self.mainFrame.appendChild(self.moduleMgr)

		self.moduleList = html5.Nav()
		self.moduleList["class"] = "vi-modulelist"
		self.moduleMgr.appendChild(self.moduleList)

		self.modulePipe = html5.Div()
		self.modulePipe.addClass("vi-modulepipe")
		self.moduleMgr.appendChild(self.modulePipe)

		self.viewport = html5.Div()
		self.viewport["class"] = "vi-viewer-frame"
		self.mainFrame.appendChild(self.viewport)

		self.logWdg = Log()
		self.appendChild(self.logWdg)

		self.currentPane = None
		self.nextPane = None  # Which pane gains focus once the deferred call fires
		self.panes = []  # List of known panes. The ordering represents the order in which the user visited them.

		self.userLoggedOutMsg = None

		# Register the error-handling for this iframe
		le = eval("window.top.logError")
		w = eval("window")
		w.onerror = le
		w = eval("window.top")
		w.onerror = le

	def onClick(self, event):
		if html5.utils.doesEventHitWidgetOrChildren(event, self.modulePipe):
			conf["mainWindow"].switchFullscreen(not conf["mainWindow"].isFullscreen())

	def reset(self):
		self.moduleList.removeAllChildren()
		self.viewport.removeAllChildren()
		self.logWdg.reset()

		self.currentPane = None
		self.nextPane = None
		self.panes = []

		if self.userLoggedOutMsg:
			self.userLoggedOutMsg.stopInterval()
			self.userLoggedOutMsg = None

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

		moduleGroups = []

		# Save module groups
		if ("configuration" in config.keys()
			and isinstance(config["configuration"], dict)):

			if ("modulGroups" in config["configuration"].keys()
				and isinstance(config["configuration"]["modulGroups"], list)):
				alert("Hello! Your project is still using 'admin.modulGroups' for its module grouping information.\n"
					  "Please rename it to 'admin.moduleGroups' (yes, with 'e') to avoid this alert message.\n\n"
					  "Thank you!")

				moduleGroups = config["configuration"]["modulGroups"]

			if ("moduleGroups" in config["configuration"].keys()
				and isinstance(config["configuration"]["moduleGroups"], list)):
				moduleGroups = config["configuration"]["moduleGroups"]

		# Modules
		groupPanes = {}
		panes = []
		userAccess = conf["currentUser"].get("access", [])
		predefinedFilterCounter = 1

		groupedModules = {}

		# First create group panes, if configured
		for group in moduleGroups:
			groupedModules[group["prefix"]]=[]
			groupPanes[group["prefix"]] = GroupPane(group["name"], iconURL=group.get("icon"))
			groupPanes[group["prefix"]].groupPrefix = group["prefix"]
			panes.append((group["name"], group.get("sortIndex"), groupPanes[group["prefix"]]))

		# read Hash to register startup module
		currentActiveGroup = None
		path = None
		urlHash = conf["startupHash"]
		if urlHash:

			if "?" in urlHash:
				hashStr = urlHash[1:urlHash.find("?")]
			else:
				hashStr = urlHash[1:]
			path = [x for x in hashStr.split("/") if x]

		sortedModules = []
		topLevelModules = {}

		for x, y in config["modules"].items():
			sortedModules.append((x, y))

			groupName = y["name"].split(":")[0] + ": "

			if groupName not in groupPanes.keys():
				topLevelModules.update({x: y})
			else:
				if path and x == path[0]:
					currentActiveGroup = groupName

				groupedModules[groupName].append((x, y))

		conf["vi.groupedModules"] = groupedModules

		sortedModules.sort(key=lambda entry: "%d-%010d-%s" % (1 if entry[1].get("sortIndex") is None else 0, entry[1].get("sortIndex", 0), entry[1].get("name")))

		# When create module panes
		for module, info in sortedModules:
			if not "root" in userAccess and not any([x.startswith(module) for x in userAccess]):
				# Skip this module, as the user couldn't interact with it anyway
				continue
			info.update({"_handler":handler})

			conf["modules"][module] = info

			if "views" in conf["modules"][module].keys() and conf["modules"][module]["views"]:
				for v in conf["modules"][module]["views"]:  # Work-a-round for PyJS not supporting id()
					v["__id"] = predefinedFilterCounter
					predefinedFilterCounter += 1


			if currentActiveGroup or module in topLevelModules:
				handlerCls = HandlerClassSelector.select(module, info)
				assert handlerCls is not None, "No handler available for module '%s'" % module

				conf["modules"][module]["visibleName"] = conf["modules"][module]["name"]
				handler = None

				if info["name"] and currentActiveGroup and info["name"].startswith(currentActiveGroup):
					conf["modules"][module]["visibleName"] = conf["modules"][module]["name"].replace(currentActiveGroup, "")
					handler = handlerCls(module, info)
					groupPanes[currentActiveGroup].addChildPane(handler)

				if not handler and module in topLevelModules:
					handler = handlerCls(module, info)
					panes.append((info["visibleName"], info.get("sortIndex"), handler))

		# Sorting our top level entries
		panes.sort(key=lambda entry: "%d-%010d-%s" % (1 if entry[1] is None else 0, entry[1] or 0, entry[0]))

		# Add panes in the created order
		for name, idx, pane in panes:
			self.addPane(pane)

		# Finalizing!
		viInitializedEvent.fire()
		DeferredCall(self.checkInitialHash)
		self.unlock()

	def log(self, type, msg, icon):
		self.logWdg.log(type, msg, icon)

	def checkInitialHash(self, *args, **kwargs):
		urlHash = conf["startupHash"]
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

	def _registerChildPanes(self, pane):
		for childPane in pane.childPanes:
			self.panes.append(childPane)
			self.viewport.appendChild(childPane.widgetsDomElm)
			childPane.widgetsDomElm.removeClass("is-active")
			self._registerChildPanes(childPane)

	def addPane(self, pane, parentPane=None):
		# paneHandle = "pane_%s" % self.paneIdx
		# self.paneIdx += 1
		if len(pane.childPanes) > 0:
			self._registerChildPanes(pane)

		self.panes.append(pane)

		if parentPane:
			parentPane.addChildPane(pane)
		else:
			self.moduleList.appendChild(pane)

		self.viewport.appendChild(pane.widgetsDomElm)
		pane.widgetsDomElm.removeClass("is-active")


	def insertPane(self, pane, insertAt):
		if len(pane.childPanes) > 0:
			self._registerChildPanes(pane)

		assert insertAt in self.panes

		self.panes.append(pane)
		self.moduleList.insertBefore(pane, insertAt)

		self.viewport.appendChild(pane.widgetsDomElm)
		pane.widgetsDomElm.removeClass("is-active")

	def stackPane(self, pane, focus=False):
		assert self.currentPane is not None, "Cannot stack a pane. There's no current one."
		self.addPane(pane, parentPane=self.currentPane)
		if focus and not self.nextPane:
			# We defer the call to focus, as some widgets stack more than one pane at once.
			# If we focus directly, they will stack on each other, instead of the pane that
			# currently has focus
			self.nextPane = pane
			DeferredCall(self.focusNextPane)

	def focusNextPane(self, *args, **kwargs):
		"""
			The deferred call just fired. Focus that pane.
		"""
		if not self.nextPane:
			return

		nextPane = self.nextPane
		self.nextPane = None

		self.focusPane(nextPane)

	def focusPane(self, pane):
		assert pane in self.panes, "Cannot focus unknown pane!"

		if not pane.focusable:
			self.topBar.setCurrentModulDescr()
			return

		# Click on the same pane?
		if pane == self.currentPane:
			if self.currentPane.collapseable:
				if self.currentPane.isExpanded:
					self.currentPane.collapse()
				else:
					self.currentPane.expand()

			return

		self.panes.remove(pane)  # Move the pane to the end of the list
		self.panes.append(pane)

		# Close current Pane
		if self.currentPane is not None:
			self.currentPane.item.removeClass("is-active")
			self.currentPane.widgetsDomElm.removeClass("is-active")

		# Focus wanted Pane
		self.topBar.setCurrentModulDescr(pane.descr, pane.iconURL, pane.iconClasses, path=pane.path)

		self.currentPane = pane
		self.currentPane.widgetsDomElm.addClass("is-active")

		if self.currentPane.collapseable and self.currentPane.childDomElem:
			self.currentPane.childDomElem["style"]["display"] = "block"
			self.currentPane.childDomElem.addClass("is-active")

		self.currentPane.item.addClass("is-active")

		# Also open parent panes, if not already done
		pane = self.currentPane.parentPane
		while isinstance(pane, Pane):
			if pane.childDomElem["style"].get("display", "none") == "none":
				pane.childDomElem["style"]["display"] = "block"

			pane = pane.parentPane

	def removePane(self, pane):
		assert pane in self.panes, "Cannot remove unknown pane!"

		self.panes.remove(pane)
		if pane == self.currentPane:
			if self.panes:
				self.focusPane(self.panes[-1])
			else:
				self.currentPane = None

		if pane == self.nextPane:
			if self.panes:
				self.nextPane = self.panes[-1]
			else:
				self.nextPane = None

		if not pane.parentPane or pane.parentPane is self:
			self.moduleList.removeChild(pane)
		else:
			pane.parentPane.removeChildPane(pane)

		self.viewport.removeChild(pane.widgetsDomElm)

	def addWidget(self, widget, pane):
		pane.addWidget(widget)

	def stackWidget(self, widget):
		assert self.currentPane is not None, "Cannot stack a widget while no pane is active"
		self.addWidget(widget, self.currentPane)

	def removeWidget(self, widget):
		for pane in self.panes:
			if pane.containsWidget(widget):
				pane.removeWidget(widget)
				return

		raise AssertionError("Tried to remove unknown widget %s" % str(widget))

	def containsWidget(self, widget):
		for pane in self.panes:
			if pane.containsWidget(widget):
				return pane

		return None
