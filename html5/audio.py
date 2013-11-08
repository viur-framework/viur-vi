from html5.widget import Widget
from html5.html5Attr.src import Src
from html5.html5Attr.media import Multimedia
class Audio( Widget,Src,Multimedia ):
	_baseClass = "audio"

	def __init__(self, *args, **kwargs):
		super(Audio,self).__init__( *args, **kwargs )
