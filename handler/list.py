import json
from network import NetworkService
from priorityqueue import HandlerClassSelector
from widgets import ListWidget
from config import conf
from pane import Pane


class ListHandler( Pane ):
	def __init__(self, modulName, modulInfo, *args, **kwargs):
		icon = None
		if "icon" in modulInfo.keys():
			icon = modulInfo["icon"]
		super( ListHandler, self ).__init__( modulInfo["name"], icon )
		self.modulName = modulName
		self.modulInfo = modulInfo
		if "views" in modulInfo.keys():
			for view in modulInfo["views"]:
				self.addChildPane( ListHandler(modulName,view) )

	@staticmethod
	def canHandle( modulName, modulInfo ):
		return( True )

	def onClick(self, *args, **kwargs ):
		if not len(self.widgetsDomElm._children):
			self.addWidget( ListWidget(self.modulName ) )
		super( ListHandler, self ).onClick( *args, **kwargs )


HandlerClassSelector.insert( 1, ListHandler.canHandle, ListHandler )
