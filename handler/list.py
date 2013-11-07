import json
from network import NetworkService
from priorityqueue import HandlerClassSelector
from widgets import ListWidget
from config import conf
from pane import Pane


class ListHandler( Pane ):
	def __init__(self, modulName, modulInfo, *args, **kwargs):
		print("INIT LISTHANDLER")
		super( ListHandler, self ).__init__( modulName )
		self.modulName = modulName



	@staticmethod
	def canHandle( modulName, modulInfo ):
		return( True )

	def onClick(self, *args, **kwargs ):
		print("CLICK")
		if not len(self.widgetsDomElm._children):
			print("ADDING WIDGET")
			self.addWidget( ListWidget(self.modulName ) )
		super( ListHandler, self ).onClick( *args, **kwargs )


HandlerClassSelector.insert( 1, ListHandler.canHandle, ListHandler )
