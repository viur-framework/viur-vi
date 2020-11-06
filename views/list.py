from flare.views.view import View, ViewWidget
from vi.priorityqueue import HandlerClassSelector, moduleWidgetSelector

class listHandler(View):

	def __init__(self):
		dictOfWidgets = {
			"viewport"     : listHandlerWidget
		}
		super().__init__(dictOfWidgets)

	@staticmethod
	def canHandle( moduleName, moduleInfo ):
		return moduleInfo[ "handler" ] == "list" or moduleInfo[ "handler" ].startswith( "list." )

HandlerClassSelector.insert(1, listHandler.canHandle, listHandler)

class listHandlerWidget(ViewWidget):

	def initWidget( self ):
		'''
			Here we start!
		'''
		self.addClass( [ "vi-viewer-pane", "is-active" ] )
		self.moduleInfo = self.view.params["data"]
		self.moduleName = self.view.params["moduleName"]

		widgen = moduleWidgetSelector.select(self.moduleName, self.moduleInfo)
		widget = widgen(self.moduleName,**self.moduleInfo)
		self.appendChild(widget)