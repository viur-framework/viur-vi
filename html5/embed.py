from html5.widget import Widget

class Embed( Widget):
	_baseClass = "embed"

	def __init__(self, *args, **kwargs):
		super(Embed,self).__init__( *args, **kwargs )


	def _getWidth(self):
		return self.element.width
	def _setWidth(self,val):
		self.element.width=val

	def _getHeight(self):
		return self.element.height
	def _setHeight(self,val):
		self.element.height=val

	def _getType(self):
		return self.element.type
	def _setType(self,val):
		self.element.type=val

	def _getSrc(self):
		return self.element.src
	def _setSrc(self,val):
		self.element.src=val