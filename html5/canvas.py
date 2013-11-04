from html5.widget import Widget

class Canvas( Widget):
	_baseClass = "canvas"

	def __init__(self, *args, **kwargs):
		super(Canvas,self).__init__( *args, **kwargs )


	def _getWidth(self):
		return self.element.width
	def _setWidth(self,val):
		self.element.width=val

	def _getHeight(self):
		return self.element.height
	def _setHeight(self,val):
		self.element.height=val
