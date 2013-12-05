class TextNode( object ):
	"""
		Represents a piece of text inside the DOM.
		This is the *only* object not deriving from "Widget", as it does
		not support any of its properties.
	"""

	def __init__(self, txt=None, *args, **kwargs ):
		super( TextNode, self ).__init__()
		self._children = []
		self.element = eval("document.createTextNode('')")
		if txt is not None:
			self.element.data = txt

	"""
	def __len__(self):
		return( len(self.element.data ))

	def __add__(self, other):
		if not isinstance( other, str ):
			raise ValueError("Cannot concatenate TextNode and %s" % str(type(other)))
	"""

	def setText(self,txt):
		self.element.data = txt

	def getText(self):
		return( self.element.data )

	def __str__(self):
		return( self.element.data )

	def onAttach(self):
		pass

	def onDetach(self):
		pass
