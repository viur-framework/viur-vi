from priorityqueue import HandlerClassSelector
from widgets import TreeWidget
from config import conf
from pane import Pane


class TreeHandler( Pane ):
	def __init__(self, modulName, modulInfo, *args, **kwargs):
		super( TreeHandler, self ).__init__( modulName )
		self.modulName = modulName



	@staticmethod
	def canHandle( modulName, modulInfo ):
		return( modulInfo["handler"]=="tree" or modulInfo["handler"].startswith("tree."))

	def onClick(self, *args, **kwargs ):
		print("CLICK TREE")
		if not len(self.widgetsDomElm._children):
			self.addWidget( TreeWidget(self.modulName ) )
		super( TreeHandler, self ).onClick()


HandlerClassSelector.insert( 3, TreeHandler.canHandle, TreeHandler )
