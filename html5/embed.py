from html5.widget import Widget
from html5.html5Attr.src import Src
from html5.html5Attr.media import Type,Dimensions
class Embed( Widget,Src,Type,Dimensions):
	_baseClass = "embed"

	def __init__(self, *args, **kwargs):
		super(Embed,self).__init__( *args, **kwargs )