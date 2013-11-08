from html5.widget import Widget
from html5.html5Attr.src import Src
from html5.html5Attr.media import Dimensions,Multimedia
class Video( Widget,Src,Dimensions,Multimedia ):
	_baseClass = "video"

	def __init__(self, *args, **kwargs):
		super(Video,self).__init__( *args, **kwargs )

	def _getPoster(self):
		return self.element.poster
	def _setPoster(self,val):
		self.element.poster=val

