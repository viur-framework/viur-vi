from vi.widgets.tree import TreeWidget
from vi.widgets.list import ListWidget
from vi.config import conf

from vi.priorityqueue import displayDelegateSelector, moduleWidgetSelector

class HierarchyWidget(TreeWidget):
	'''
		ein Tree mit deaktivierten leafs.
	'''
	leafWidget = None

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.listview = None
		self.listwidgetadded = False
		self.listviewActive = False

	def buildSideWidget(self):
		# listview
		self.listview = ListWidget( self.module, context = self.context, autoload = False )
		self.listview.actionBar.setActions( [ "preview", "selectfields" ], widget = self )
		self.listwidgetadded = False
		self.listviewActive = False
		self.setListView( self.listviewActive )

	def reloadData( self ):
		super(HierarchyWidget,self).reloadData()

		if self.listviewActive and not self.listwidgetadded:
			self.listwidgetadded = True
			conf[ "mainWindow" ].stackWidget( self.listview, disableOtherWidgets = False )

		if self.listviewActive:
			self.reloadListWidget()

	def reloadListWidget( self ):
		listfilter = {  "orderby": "sortindex", "skelType": "node" }

		if self.currentSelectedElements:
			listfilter.update({"parententry": self.currentSelectedElements[0].data["key"]})
		else:
			listfilter.update( { "parententry": self.rootNode } )
		self.listview.setFilter( listfilter )

	def toggleListView( self ):
		self.setListView( not self.listviewActive )
		self.reloadData()

	def setListView( self, visible = False ):
		if visible:
			self[ "style" ][ "width" ] = "50%"
			self.listviewActive = True
			self.showListView()
			return
		self.listviewActive = False
		self.hideListView()
		self[ "style" ][ "width" ] = "100%"

	def showListView( self ):
		self.listview.show()

	def hideListView( self ):
		self.listview.hide()

	def onSelectionChanged( self, widget, selection ):
		if self.listviewActive:
			self.reloadData()

	@staticmethod
	def canHandle( moduleName, moduleInfo ):
		return moduleInfo[ "handler" ] == "hierarchy" or moduleInfo[ "handler" ].startswith( "hierarchy." )


moduleWidgetSelector.insert(1, HierarchyWidget.canHandle, HierarchyWidget)
displayDelegateSelector.insert(1, HierarchyWidget.canHandle, HierarchyWidget)
