from flare.views.view import View, ViewWidget

class NotFound(View):

	def __init__(self):
		dictOfWidgets = {
			"viewport"     : NotFoundWidget
		}
		super().__init__(dictOfWidgets)

class NotFoundWidget(ViewWidget):

	def initWidget( self ):
		'''
			Here we start!
		'''

		self.appendChild('''Not Found''')