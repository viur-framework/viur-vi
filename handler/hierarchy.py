from priorityqueue import HandlerClassSelector
from widgets import HierarchyWidget
from config import conf
from pane import Pane


class HierarchyHandler( Pane ):
	def __init__(self, modulName, modulInfo, *args, **kwargs):
		super( HierarchyHandler, self ).__init__( modulInfo["name"] )
		self.modulName = modulName



	@staticmethod
	def canHandle( modulName, modulInfo ):
		return( modulInfo["handler"]=="hierarchy" or modulInfo["handler"].startswith("hierarchy."))

	def onClick(self, *args, **kwargs ):
		print("CLICK TREE")
		if not len(self.widgetsDomElm._children):
			self.addWidget( HierarchyWidget(self.modulName ) )
		super( HierarchyHandler, self ).onClick( *args, **kwargs )


HandlerClassSelector.insert( 3, HierarchyHandler.canHandle, HierarchyHandler )
