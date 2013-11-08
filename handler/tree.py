from priorityqueue import HandlerClassSelector, displayDelegateSelector
from widgets import TreeWidget
from config import conf
from pane import Pane


class TreeHandler( Pane ):
	def __init__(self, modulName, modulInfo, *args, **kwargs):
		super( TreeHandler, self ).__init__( modulName )
		self.modulName = modulName
		self.modulInfo = modulInfo


	@staticmethod
	def canHandle( modulName, modulInfo ):
		return( modulInfo["handler"]=="tree" or modulInfo["handler"].startswith("tree."))

	def onClick(self, *args, **kwargs ):
		print("CLICK TREE")
		if not len(self.widgetsDomElm._children):
			wdg = displayDelegateSelector.select( self.modulName, self.modulInfo )
			assert wdg is not None, "Got no handler for %s" % self.modulName
			self.addWidget( wdg(self.modulName ) )
		super( TreeHandler, self ).onClick( *args, **kwargs )


HandlerClassSelector.insert( 3, TreeHandler.canHandle, TreeHandler )
