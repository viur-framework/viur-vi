from html5.widget import Widget

class Blockquote( Widget):
	_baseClass = "blockquote"

	def __init__(self, *args, **kwargs):
		super(Blockquote,self).__init__( *args, **kwargs )

	def _getBlockquote(self):
		return self.element.blockquote
	def _setBlockquote(self,val):
		self.element.blockquote=val