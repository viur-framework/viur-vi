from html5.a import A

class Area( A ):
	_baseClass = "area"

	def __init__(self, *args, **kwargs):
		super(Area,self).__init__( *args, **kwargs )

	def _getCoords(self):
		return self.element.coords
	def _setCoords(self,val):
		self.element.coords=val

	def _getAlt(self):
		return self.element.alt
	def _setAlt(self,val):
		self.element.alt=val

	def _getShape(self):
		return self.element.shape
	def _setShape(self,val):
		self.element.shape=val

