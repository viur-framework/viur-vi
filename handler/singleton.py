from priorityqueue import HandlerClassSelector, displayDelegateSelector, initialHashHandler
from widgets import EditWidget
from config import conf
from pane import Pane


class SingletonHandler( Pane ):
	def __init__(self, modulName, modulInfo, *args, **kwargs):
		icon = "icons/modules/singleton.svg"
		if "icon" in modulInfo.keys():
			icon = modulInfo["icon"]
		super( SingletonHandler, self ).__init__( modulInfo["name"], icon )
		self.modulName = modulName
		self.modulInfo = modulInfo
		initialHashHandler.insert( 1, self.canHandleInitialHash, self.handleInitialHash)

	def canHandleInitialHash(self, pathList ):
		if len(pathList)>1:
			if pathList[0]==self.modulName and pathList[1]=="edit":
				return( True )
		return( False )

	def handleInitialHash(self, pathList):
		assert self.canHandleInitialHash( pathList )
		edwg = EditWidget( self.modulName, EditWidget.appSingleton)
		self.addWidget( edwg )
		self.focus()

	@staticmethod
	def canHandle( modulName, modulInfo ):
		return( modulInfo["handler"]=="singleton" or modulInfo["handler"].startswith("singleton."))

	def onClick(self, *args, **kwargs ):
		if not len(self.widgetsDomElm._children):
			self.addWidget( EditWidget( modul=self.modulName, applicationType=EditWidget.appSingleton ) )
		super( SingletonHandler, self ).onClick( *args, **kwargs )


HandlerClassSelector.insert( 3, SingletonHandler.canHandle, SingletonHandler )
