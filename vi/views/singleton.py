from flare.views.view import View, ViewWidget
from vi.priorityqueue import HandlerClassSelector, ModuleWidgetSelector
from vi.widgets.edit import EditWidget
from vi.config import conf

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
		self.data = self.view.params[ "data" ]
		self.moduleName = self.view.params[ "moduleName" ]

		context = self.data.get("context", None)
		clone = self.data.get("clone", False)
		baseType = EditWidget.appSingleton

		widget = EditWidget(
			self.moduleName, baseType,
			context=context,
			clone=clone
		)

		self.appendChild(widget)

	def onViewfocusedChanged( self, viewname, *args, **kwargs ):
		conf["theApp"].setPath(self.moduleName + "/edit")
