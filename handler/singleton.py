from priorityqueue import HandlerClassSelector, displayDelegateSelector
from widgets import EditWidget
from config import conf
from pane import Pane


class SingletonHandler( Pane ):
	def __init__(self, modulName, modulInfo, *args, **kwargs):
		super( SingletonHandler, self ).__init__( modulInfo["name"] )
		self.modulName = modulName
		self.modulInfo = modulInfo


	@staticmethod
	def canHandle( modulName, modulInfo ):
		return( modulInfo["handler"]=="singleton" or modulInfo["handler"].startswith("singleton."))

	def onClick(self, *args, **kwargs ):
		if not len(self.widgetsDomElm._children):
			self.addWidget( EditWidget( modul=self.modulName, applicationType=EditWidget.appSingleton ) )
		super( SingletonHandler, self ).onClick( *args, **kwargs )


HandlerClassSelector.insert( 3, SingletonHandler.canHandle, SingletonHandler )
