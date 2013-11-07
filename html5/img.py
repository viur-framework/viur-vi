from html5 import Widget

class Img( Widget ):
	_baseClass = "img"

	def __init__(self, src=None, *args, **kwargs ):
		super( Img, self ).__init__( *args, **kwargs )
		if src is not None:
			self["src"] = src

	def _getSrc(self):
		return( self.element )

	def _setSrc(self, val):
		self.element.src = val