from html5.a import A
from html5.html5Attr.form import Alt
class Area( A,Alt ):
	_baseClass = "area"

	def __init__(self, *args, **kwargs):
		super(Area,self).__init__( *args, **kwargs )

	def _getCoords(self):
		return self.element.coords
	def _setCoords(self,val):
		self.element.coords=val

	def _getShape(self):
		return self.element.shape
	def _setShape(self,val):
		self.element.shape=val

