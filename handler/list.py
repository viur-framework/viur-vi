# -*- coding: utf-8 -*-
from vi.network import NetworkService, DeferredCall
from vi.priorityqueue import HandlerClassSelector, initialHashHandler
from vi.config import conf
from vi.pane import Pane
from vi.widgets.edit import EditWidget
from vi.i18n import translate
from vi.priorityqueue import moduleWidgetSelector

class ListHandler(Pane):
	def __init__(self, moduleName, moduleInfo, isView=False, wasRequested = False, *args, **kwargs):

		icon = "icons-list"
		if "icon" in moduleInfo.keys():
			icon = moduleInfo["icon"]

		super(ListHandler, self).__init__(moduleInfo.get("visibleName", moduleInfo["name"]), icon,path=moduleName + "/list" if not wasRequested else None)

		self.moduleName = moduleName
		self.moduleInfo = moduleInfo

		self.mode = moduleInfo.get("mode", "normal")
		assert self.mode in ["normal", "hidden", "group"]

		self.wasRequested = wasRequested
		self.requestedViews = None

		if self.mode == "hidden" or moduleInfo.get("hideInMainBar", False):
			self.hide()
		elif "views" in self.moduleInfo:
			#DeferredCall(self._buildViewPanes, self.moduleInfo["views"])
			self._buildViewPanes(self.moduleInfo["views"])

		if not isView:
			initialHashHandler.insert(1, self.canHandleInitialHash, self.handleInitialHash)

	def _buildViewPanes(self, views, register=False, requested=False):
		for view in views:
			# Extend some inherited attributes from moduleInfo, if not overridden
			for inherit in ["+name", "+columns", "+filter", "+context", "+actions", "+handler"]:
				if inherit in view:
					inherit = inherit[1:]

					if inherit in self.moduleInfo:
						if isinstance(self.moduleInfo[inherit], list):
							assert isinstance(view["+" + inherit], list)

							if inherit not in view:
								view[inherit] = self.moduleInfo[inherit][:]

							view[inherit].extend(view["+" + inherit])
						elif isinstance(self.moduleInfo[inherit], dict):
							assert isinstance(view["+" + inherit], dict)

							if inherit not in view:
								view[inherit] = self.moduleInfo[inherit].copy()

							view[inherit].update(view["+" + inherit])

						else:
							view[inherit] = self.moduleInfo[inherit] + view["+" + inherit]

					else:
						view[inherit] = view["+" + inherit]

					del view["+" + inherit]

			# Inherit some default attributes from moduleInfo, if not overridden or extended
			for inherit in ["icon", "columns", "filter", "context", "handler"]:
				if inherit not in view and inherit in self.moduleInfo:
					view[inherit] = self.moduleInfo[inherit]

			pane = ListHandler(self.moduleName, view, isView=True, wasRequested=requested)

			self.isExpanded=False
			if self.childDomElem:
				self.childDomElem.hide()

			if not register:
				#print("adding pane %s to %s" % (pane.moduleInfo.get("name"), self.moduleInfo.get("name")))
				self.addChildPane(pane)
			else:
				#print("adding pane %s to mainWindow" % pane.moduleInfo.get("name"))
				conf["mainWindow"].addPane(pane, self)

	def canHandleInitialHash(self, pathList, params):
		if len(pathList) > 1:
			if pathList[0] == self.moduleName:
				if pathList[1] in ["add", "list"] or (pathList[1] in ["edit", "clone"] and len(pathList) > 2):
					return True

		return False

	def _createWidget(self):
		widgen = moduleWidgetSelector.select(self.moduleName, self.moduleInfo)
		assert widgen

		return widgen(
			self.moduleName,
			**self.moduleInfo
		)

	def handleInitialHash(self, pathList, params):
		assert self.canHandleInitialHash(pathList, params)

		if pathList[1] == "list":
			self.addWidget(self._createWidget())
			self.focus()

		elif pathList[1] == "add":
			pane = Pane(translate("Add"), closeable=True, iconURL="icons-add",
			            iconClasses=["module_%s" % self.moduleName, "apptype_list", "action_add"])
			edwg = EditWidget(self.moduleName, EditWidget.appList, hashArgs=(params or None))
			pane.addWidget(edwg)
			conf["mainWindow"].addPane(pane, parentPane=self)
			pane.focus()

		elif pathList[1] in ["edit", "clone"] and len(pathList) > 2:
			pane = Pane(translate("Edit"), closeable=True, iconURL="icons-edit",
			            iconClasses=["module_%s" % self.moduleName, "apptype_list", "action_edit"])
			edwg = EditWidget(self.moduleName, EditWidget.appList, key=pathList[2], hashArgs=(params or None), clone=pathList[1] == "clone")
			pane.addWidget(edwg)
			conf["mainWindow"].addPane(pane, parentPane=self)
			pane.focus()

	@staticmethod
	def canHandle(moduleName, moduleInfo):
		return moduleInfo["handler"] == "list" or moduleInfo["handler"].startswith("list.")

	def onClick(self, *args, **kwargs):
		if self.mode == "normal" and not self.widgetsDomElm.children():
			self.addWidget(self._createWidget())

		''' no time right now...
		if self.childDomElem is None and "views" in self.moduleInfo:
			self.lock()
			self._buildViewPanes(self.moduleInfo["views"])
			self.unlock()
		'''

		if self.requestedViews is None and "views.request" in self.moduleInfo:
			self.lock()

			NetworkService.request(
				self.moduleName,
				self.moduleInfo["views.request"],
				successHandler=self._onRequestViewsAvailable
			)

		super(ListHandler, self).onClick(*args, **kwargs)

	def _onRequestViewsAvailable(self, req):
		self.requestedViews = NetworkService.decode(req)
		self._buildViewPanes(self.requestedViews, register=True, requested=True)

		self.unlock()

		if not self.isExpanded:
			if self.mode == "normal":
				super(ListHandler, self).onClick()
			elif self.childPanes:
				self.childPanes[0].onClick()


HandlerClassSelector.insert(1, ListHandler.canHandle, ListHandler)
