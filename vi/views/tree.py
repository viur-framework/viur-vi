from flare.views.view import View, ViewWidget
from vi.priorityqueue import HandlerClassSelector,ModuleWidgetSelector

class treeHandler(View):

	def __init__(self):
		dictOfWidgets = {
			"viewport"     : treeHandlerWidget
		}
		super().__init__(dictOfWidgets)

	@staticmethod
	def canHandle( moduleName, moduleInfo ):
		return moduleInfo["handler"] == "tree" or moduleInfo["handler"].startswith("tree.")

HandlerClassSelector.insert(1, treeHandler.canHandle, treeHandler)

class treeHandlerWidget(ViewWidget):

	def initWidget( self ):
		'''
			Here we start!
		'''
		self.addClass(["vi-viewer-pane","is-active"])
		self.moduleInfo = self.view.params[ "data" ]
		self.moduleName = self.view.params[ "moduleName" ]

		widgen = ModuleWidgetSelector.select( self.moduleName, self.moduleInfo )
		widget = widgen( self.moduleName, **self.moduleInfo )
		self.appendChild( widget )
