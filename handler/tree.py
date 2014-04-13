from priorityqueue import HandlerClassSelector, displayDelegateSelector, initialHashHandler
from widgets import TreeWidget
from config import conf
from pane import Pane
from widgets.edit import EditWidget

from i18n import translate
class TreeHandler( Pane ):
	def __init__(self, modulName, modulInfo, *args, **kwargs):
		icon = "icons/modules/tree.svg"
		if "icon" in modulInfo.keys():
			icon = modulInfo["icon"]
		super( TreeHandler, self ).__init__( modulInfo["name"], icon )
		self.modulName = modulName
		self.modulInfo = modulInfo
		initialHashHandler.insert( 1, self.canHandleInitialHash, self.handleInitialHash)

	def canHandleInitialHash(self, pathList ):
		if len(pathList)>1:
			if pathList[0]==self.modulName:
				if pathList[1] in ["list"] or (pathList[1]=="edit" and len(pathList)>3 and pathList[2] in ["node","leaf"]):
					return( True )
		return( False )

	def handleInitialHash(self, pathList):
		assert self.canHandleInitialHash( pathList )
		if pathList[1] == "list":
			wdg = displayDelegateSelector.select( self.modulName, self.modulInfo )
			assert wdg is not None, "Got no handler for %s" % self.modulName
			self.addWidget( wdg(self.modulName ) )
			self.focus()
		elif pathList[1] == "edit" and len(pathList)>3:
			pane = Pane(translate("Edit"), closeable=True, iconClasses=["modul_%s" % self.modulName, "apptype_tree", "action_edit" ])
			edwg = EditWidget( self.modulName, EditWidget.appTree, key=pathList[3], skelType=pathList[2])
			pane.addWidget( edwg )
			conf["mainWindow"].addPane( pane, parentPane=self)
			pane.focus()

	@staticmethod
	def canHandle( modulName, modulInfo ):
		return( modulInfo["handler"]=="tree" or modulInfo["handler"].startswith("tree."))

	def onClick(self, *args, **kwargs ):
		if not len(self.widgetsDomElm._children):
			wdg = displayDelegateSelector.select( self.modulName, self.modulInfo )
			assert wdg is not None, "Got no handler for %s" % self.modulName
			self.addWidget( wdg(self.modulName ) )
		super( TreeHandler, self ).onClick( *args, **kwargs )


HandlerClassSelector.insert( 3, TreeHandler.canHandle, TreeHandler )
