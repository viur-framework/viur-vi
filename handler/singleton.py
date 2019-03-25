# -*- coding: utf-8 -*-
from priorityqueue import HandlerClassSelector, displayDelegateSelector, initialHashHandler
from widgets import EditWidget
from pane import Pane

class SingletonHandler( Pane ):
	def __init__(self, moduleName, moduleInfo, *args, **kwargs):
		super(SingletonHandler, self).__init__(
			moduleInfo["visibleName"],
			moduleInfo.get("icon", "icons/modules/singleton.svg")
		)

		self.moduleName = moduleName
		self.moduleInfo = moduleInfo

		if "hideInMainBar" in moduleInfo.keys() and moduleInfo["hideInMainBar"]:
			self["style"]["display"] = "none"

		initialHashHandler.insert(1, self.canHandleInitialHash, self.handleInitialHash)

	def canHandleInitialHash(self, pathList, params):
		if len(pathList) > 1:
			if pathList[0] == self.moduleName and pathList[1] == "edit":
				return True

		return False

	def handleInitialHash(self, pathList, params):
		assert self.canHandleInitialHash(pathList, params)

		self.addWidget(EditWidget(self.moduleName, EditWidget.appSingleton, hashArgs=(params or None)))
		self.focus()

	@staticmethod
	def canHandle(moduleName, moduleInfo):
		return moduleInfo["handler"]=="singleton" or moduleInfo["handler"].startswith("singleton.")

	def onClick(self, *args, **kwargs):
		if not self.widgetsDomElm.children():
			self.addWidget(EditWidget(self.moduleName, EditWidget.appSingleton))

		super(SingletonHandler, self).onClick(*args, **kwargs)

HandlerClassSelector.insert( 3, SingletonHandler.canHandle, SingletonHandler )
