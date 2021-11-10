from flare.views.view import View, ViewWidget
from vi.priorityqueue import HandlerClassSelector, moduleWidgetSelector
from vi.widgets.edit import EditWidget


class editHandler(View):

	def __init__(self):
		dictOfWidgets = {
			"viewport": editHandlerWidget
		}
		super().__init__(dictOfWidgets)


class editHandlerWidget(ViewWidget):

	def initWidget(self):
		'''
			Here we start!
		'''
		self.addClass(["vi-viewer-pane", "is-active"])
		self.data = self.view.params["data"]
		self.moduleName = self.view.params["moduleName"]

		context = self.data.get("context",None)
		akey = self.data.get("key",None)
		clone = self.data.get("clone",False)
		baseType = self.data.get("baseType",EditWidget.appList)
		node = self.data.get("node",None)
		skelType = self.data.get("skelType",None)
		group = self.data.get("group", None)


		widget = EditWidget(self.moduleName, baseType,
							skelData=self.data.get("skelData", None),
							context=context,
							key=akey,
							clone =clone,
							node = node,
							skelType=skelType,
							group=group)

		self.appendChild(widget)
