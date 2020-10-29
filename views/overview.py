from flare.views.view import View, ViewWidget

class Overview(View):

	def __init__(self):
		dictOfWidgets = {
			"viewport"     : OverviewWidget
		}
		super().__init__(dictOfWidgets)

class OverviewWidget(ViewWidget):

	def initWidget( self ):
		'''
			Here we start!
		'''

		self.appendChild('''HALLO''')