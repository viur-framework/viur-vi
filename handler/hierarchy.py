# -*- coding: utf-8 -*-
from vi.priorityqueue import HandlerClassSelector, initialHashHandler,displayDelegateSelector
from vi.widgets import HierarchyWidget
from vi.config import conf
from vi.pane import Pane
from vi.widgets.edit import EditWidget
from vi.i18n import translate
import logging

class HierarchyHandler(Pane):
	def __init__(self, moduleName, moduleInfo, *args, **kwargs):

		icon = "icons-hierarchy"
		if "icon" in moduleInfo.keys():
			icon = moduleInfo["icon"]

		super(HierarchyHandler, self).__init__(moduleInfo["visibleName"], icon,path=moduleName + "/list")

		if "hideInMainBar" in moduleInfo.keys() and moduleInfo["hideInMainBar"]:
			self["style"]["display"] = "none"

		self.moduleName = moduleName
		self.moduleInfo = moduleInfo

		initialHashHandler.insert(1, self.canHandleInitialHash, self.handleInitialHash)

	def canHandleInitialHash(self, pathList, params):
		if len(pathList) > 1:
			if pathList[0] == self.moduleName:
				if pathList[1] in ["list"] or (pathList[1] == "edit" and len(pathList) > 2):
					return (True)
		return (False)

	def handleInitialHash(self, pathList, params):
		assert self.canHandleInitialHash(pathList, params)
		if pathList[1] == "list":
			wdg = displayDelegateSelector.select( self.moduleName, self.moduleInfo )
			assert wdg is not None, "Got no handler for %s" % self.moduleName
			node = None
			if len( pathList ) >= 3 and pathList[ 2 ]:
				node = pathList[ 2 ]
			self.addWidget( wdg( self.moduleName, node = node ) )
			self.focus()

		elif pathList[1] in ["edit", "clone"] and len(pathList) > 2:
			pane = Pane(translate("Edit"), closeable=True, iconURL="icons-edit",
			            iconClasses=["module_%s" % self.moduleName, "apptype_hierarchy", "action_edit"])
			edwg = EditWidget(self.moduleName, EditWidget.appHierarchy, key=pathList[2], hashArgs=(params or None), clone=pathList[1] == "clone")
			pane.addWidget(edwg)
			conf["mainWindow"].addPane(pane, parentPane=self)
			pane.focus()

	@staticmethod
	def canHandle(moduleName, moduleInfo):
		return moduleInfo["handler"] == "hierarchy" or moduleInfo["handler"].startswith("hierarchy.")

	def onClick(self, *args, **kwargs):
		if not len(self.widgetsDomElm._children):
			self.addWidget(HierarchyWidget(self.moduleName))
		super(HierarchyHandler, self).onClick(*args, **kwargs)


HandlerClassSelector.insert(3, HierarchyHandler.canHandle, HierarchyHandler)
