from flare.views.view import View, ViewWidget
from vi.priorityqueue import HandlerClassSelector,moduleWidgetSelector

class singletonHandler(View):

	def __init__(self):
		dictOfWidgets = {
			"viewport"     : singletonHandlerWidget
		}
		super().__init__(dictOfWidgets)

	@staticmethod
	def canHandle( moduleName, moduleInfo ):
		return moduleInfo["handler"]=="singleton" or moduleInfo["handler"].startswith("singleton.")

HandlerClassSelector.insert(1, singletonHandler.canHandle, singletonHandler)

class singletonHandlerWidget(ViewWidget):

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