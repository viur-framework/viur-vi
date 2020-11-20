from flare.views.view import View, ViewWidget
from vi.priorityqueue import HandlerClassSelector, moduleWidgetSelector
from vi.log import logWidget


class logHandler(View):

	def __init__(self):
		dictOfWidgets = {
			"viewport"     : logHandlerWidget
		}
		super().__init__(dictOfWidgets)

class logHandlerWidget(ViewWidget):

	def initWidget( self ):
		'''
			Here we start!
		'''



		self.logslist = self.view.params["data"]["logslist"]
		print(self.logslist)
		if not self.logslist:
			return -1
		logwdgt = logWidget( self.logslist )
		self.appendChild(logwdgt)