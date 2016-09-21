from priorityqueue import HandlerClassSelector, displayDelegateSelector, initialHashHandler
from widgets import EditWidget
from pane import Pane

class SingletonHandler( Pane ):
	def __init__(self, moduleName, modulInfo, *args, **kwargs):
		icon = "icons/modules/singleton.svg"

		if "icon" in modulInfo.keys():
			icon = modulInfo["icon"]

		super(SingletonHandler, self).__init__(modulInfo["visibleName"], icon)

		self.moduleName = moduleName
		self.modulInfo = modulInfo

		if "hideInMainBar" in modulInfo.keys() and modulInfo["hideInMainBar"]:
			self["style"]["display"] = "none"

		initialHashHandler.insert(1, self.canHandleInitialHash, self.handleInitialHash)

	def canHandleInitialHash(self, pathList, params ):
		if len(pathList) > 1:
			if pathList[0] == self.moduleName and pathList[1] == "edit":
				return True

		return False

	def handleInitialHash(self, pathList, params):
		assert self.canHandleInitialHash(pathList, params)

		self.addWidget(EditWidget(self.moduleName, EditWidget.appSingleton, hashArgs=(params or None)))
		self.focus()

	@staticmethod
	def canHandle( moduleName, modulInfo ):
		return modulInfo["handler"]=="singleton" or modulInfo["handler"].startswith("singleton.")

	def onClick(self, *args, **kwargs ):
		if not self.widgetsDomElm.children():
			self.addWidget(EditWidget(self.moduleName, EditWidget.appSingleton))

		super(SingletonHandler, self).onClick(*args, **kwargs)

HandlerClassSelector.insert( 3, SingletonHandler.canHandle, SingletonHandler )
