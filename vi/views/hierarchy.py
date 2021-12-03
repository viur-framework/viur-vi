from flare import html5
from flare.views.view import View, ViewWidget
from vi.priorityqueue import HandlerClassSelector, ModuleWidgetSelector

class hierarchyHandler(View):

	def __init__(self):
		dictOfWidgets = {
			"viewport"     : hierarchyHandlerWidget
		}
		super().__init__(dictOfWidgets)

	@staticmethod
	def canHandle( moduleName, moduleInfo ):
		return moduleInfo["handler"] == "hierarchy" or moduleInfo["handler"].startswith("hierarchy.") or  moduleInfo["handler"].startswith("tree.hierarchy")

HandlerClassSelector.insert(1, hierarchyHandler.canHandle, hierarchyHandler)

class hierarchyHandlerWidget(ViewWidget):

	def initWidget( self ):
		'''
			Here we start!
		'''
		self.mainView =html5.Div()

		self.addClass( [ "vi-viewer-pane", "is-active" ] )
		self.moduleInfo = self.view.params[ "data" ]
		self.moduleName = self.view.params[ "moduleName" ]

		widgen = ModuleWidgetSelector.select( self.moduleName, self.moduleInfo )
		widget = widgen( self.moduleName, **self.moduleInfo )
		self.appendChild( widget )