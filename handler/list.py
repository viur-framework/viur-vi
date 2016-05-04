import json
from network import NetworkService
from priorityqueue import HandlerClassSelector, initialHashHandler
from widgets import ListWidget
from config import conf
from pane import Pane
from widgets.edit import EditWidget
from i18n import translate

class ListHandler( Pane ):
	def __init__(self, modulName, modulInfo, *args, **kwargs):
		icon = "icons/modules/list.svg"
		if "icon" in modulInfo.keys():
			icon = modulInfo["icon"]

		super(ListHandler, self).__init__(modulInfo.get("visibleName", modulInfo["name"]), icon)

		self.modulName = modulName
		self.modulInfo = modulInfo

		if "hideInMainBar" in modulInfo.keys() and modulInfo["hideInMainBar"]:
			self["style"]["display"] = "none"
		else:
			if "views" in modulInfo.keys():
				for view in modulInfo["views"]:
					self.addChildPane( ListHandler(modulName,view) )

		initialHashHandler.insert(1, self.canHandleInitialHash, self.handleInitialHash)

	def canHandleInitialHash(self, pathList, params ):
		if len(pathList)>1:
			if pathList[0]==self.modulName:
				if pathList[1] in ["add","list"] or (pathList[1]=="edit" and len(pathList)>2):
					return( True )
		return( False )

	def handleInitialHash(self, pathList, params):
		assert self.canHandleInitialHash( pathList, params )
		if pathList[1] == "list":
			filter = None
			columns = None
			if "filter" in self.modulInfo.keys():
				filter = self.modulInfo["filter"]
			if "columns" in self.modulInfo.keys():
				columns = self.modulInfo["columns"]
			self.addWidget( ListWidget( self.modulName, filter=filter, columns=columns ) )
			self.focus()
		elif pathList[1] == "add":
			pane = Pane(translate("Add"), closeable=True, iconClasses=["modul_%s" % self.modulName, "apptype_list", "action_add" ])
			edwg = EditWidget( self.modulName, EditWidget.appList, hashArgs=(params or None) )
			pane.addWidget( edwg )
			conf["mainWindow"].addPane( pane, parentPane=self)
			pane.focus()
		elif pathList[1] == "edit" and len(pathList)>2:
			pane = Pane(translate("Edit"), closeable=True, iconClasses=["modul_%s" % self.modulName, "apptype_list", "action_edit" ])
			edwg = EditWidget( self.modulName, EditWidget.appList, key=pathList[2], hashArgs=(params or None))
			pane.addWidget( edwg )
			conf["mainWindow"].addPane( pane, parentPane=self)
			pane.focus()

	@staticmethod
	def canHandle( modulName, modulInfo ):
		return( modulInfo["handler"]=="list" or modulInfo["handler"].startswith("list."))

	def onClick(self, *args, **kwargs ):
		if not len(self.widgetsDomElm._children):
			filter = None
			columns = None

			if "filter" in self.modulInfo.keys():
				filter = self.modulInfo["filter"]

			if "columns" in self.modulInfo.keys():
				columns = self.modulInfo["columns"]

			self.addWidget(ListWidget(self.modulName, filter=filter,
			                            columns=columns, filterID=self.modulInfo.get("__id"),
			                            filterDescr=self.modulInfo.get("visibleName", "")))

		super(ListHandler, self).onClick(*args, **kwargs)


HandlerClassSelector.insert( 1, ListHandler.canHandle, ListHandler )
