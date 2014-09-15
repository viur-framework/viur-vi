from html5.widget import Widget
from html5.html5Attr.href import Href
from html5.html5Attr.media import Media
from html5.html5Attr.rel import Rel

class Link( Widget,Href,Media,Rel ):
	_baseClass = "link"

	def __init__(self, *args, **kwargs):
		super(Link,self).__init__( *args, **kwargs )

	def _getSizes(self):
		return self.element.sizes
	def _setSizes(self,val):
		self.element.sizes=val



