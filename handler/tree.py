# -*- coding: utf-8 -*-
from priorityqueue import HandlerClassSelector, displayDelegateSelector, initialHashHandler
from config import conf
from pane import Pane
from widgets.edit import EditWidget
from i18n import translate

class TreeHandler(Pane):
	def __init__(self, moduleName, moduleInfo, *args, **kwargs):
		super(TreeHandler, self).__init__(
			moduleInfo["visibleName"],
			moduleInfo.get("icon", "icons/modules/tree.svg"),
			path=moduleName + "/list"
		)

		self.moduleName = moduleName
		self.moduleInfo = moduleInfo

		if "hideInMainBar" in moduleInfo.keys() and moduleInfo["hideInMainBar"]:
			self["style"]["display"] = "none"

		initialHashHandler.insert(1, self.canHandleInitialHash, self.handleInitialHash)

	def canHandleInitialHash(self, pathList, params):
		if len(pathList) > 1:
			if pathList[0] == self.moduleName:
				if pathList[1] in ["list"] or (
						pathList[1] in ["edit", "clone"] and len(pathList) > 3 and pathList[2] in ["node", "leaf"]):
					return True

		return False

	def handleInitialHash(self, pathList, params):
		assert self.canHandleInitialHash(pathList, params)

		if pathList[1] == "list":
			wdg = displayDelegateSelector.select(self.moduleName, self.moduleInfo)
			assert wdg is not None, "Got no handler for %s" % self.moduleName
			self.addWidget(wdg(self.moduleName))
			self.focus()

		elif pathList[1] in ["edit", "clone"] and len(pathList) > 3:
			pane = Pane(translate("Edit"), closeable=True,
			            iconClasses=["module_%s" % self.moduleName, "apptype_tree", "action_edit"])
			edwg = EditWidget(self.moduleName, EditWidget.appTree, key=pathList[3], skelType=pathList[2],
			                  hashArgs=(params or None), clone=pathList[1] == "clone")
			pane.addWidget(edwg)
			conf["mainWindow"].addPane(pane, parentPane=self)
			pane.focus()

	@staticmethod
	def canHandle(moduleName, moduleInfo):
		return moduleInfo["handler"] == "tree" or moduleInfo["handler"].startswith("tree.")

	def onClick(self, *args, **kwargs):
		if not len(self.widgetsDomElm._children):
			wdg = displayDelegateSelector.select(self.moduleName, self.moduleInfo)
			assert wdg is not None, "Got no handler for %s" % self.moduleName
			self.addWidget(wdg(self.moduleName))

		super(TreeHandler, self).onClick(*args, **kwargs)


HandlerClassSelector.insert(3, TreeHandler.canHandle, TreeHandler)
