from html5.widget import Widget
from html5.html5Attr.src import Src
from html5.html5Attr.form import Alt
from html5.html5Attr.media import Dimensions,Usemap
class Img( Widget,Src,Dimensions,Usemap,Alt ):
	_baseClass = "img"

	def __init__(self, src=None, *args, **kwargs ):
		super( Img, self ).__init__( *args, **kwargs )
		if src is not None:
			self["src"] = src

	def _getCrossorigin(self):
		return self.element.crossorigin
	def _setCrossorigin(self,val):
		self.element.crossorigin=val

	def _getIsmap(self):
		return self.element.ismap
	def _setIsmap(self,val):
		self.element.ismap=val

