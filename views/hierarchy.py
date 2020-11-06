from flare.views.view import View, ViewWidget
from vi.priorityqueue import HandlerClassSelector, moduleWidgetSelector

class hierarchyHandler(View):

	def __init__(self):
		dictOfWidgets = {
			"viewport"     : hierarchyHandlerWidget
		}
		super().__init__(dictOfWidgets)

	@staticmethod
	def canHandle( moduleName, moduleInfo ):
		return moduleInfo["handler"] == "hierarchy" or moduleInfo["handler"].startswith("hierarchy.")

HandlerClassSelector.insert(1, hierarchyHandler.canHandle, hierarchyHandler)

class hierarchyHandlerWidget(ViewWidget):

	def initWidget( self ):
		'''
			Here we start!
		'''
		self.addClass( [ "vi-viewer-pane", "is-active" ] )
		self.moduleInfo = self.view.params[ "data" ]
		self.moduleName = self.view.params[ "moduleName" ]

		widgen = moduleWidgetSelector.select( self.moduleName, self.moduleInfo )
		widget = widgen( self.moduleName, **self.moduleInfo )
		self.appendChild( widget )