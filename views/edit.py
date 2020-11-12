from flare.views.view import View, ViewWidget
from vi.priorityqueue import HandlerClassSelector, moduleWidgetSelector
from vi.widgets.edit import EditWidget

class editHandler(View):

	def __init__(self):
		dictOfWidgets = {
			"viewport"     : editHandlerWidget
		}
		super().__init__(dictOfWidgets)

class editHandlerWidget(ViewWidget):

	def initWidget( self ):
		'''
			Here we start!
		'''
		self.addClass( [ "vi-viewer-pane", "is-active" ] )
		self.data= self.view.params["data"]
		self.moduleName = self.view.params["moduleName"]

		context = self.data.get("context",None)

		widget = EditWidget(self.moduleName, EditWidget.appList, context=context)
		self.appendChild(widget)