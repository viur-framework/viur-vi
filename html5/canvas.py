from html5.widget import Widget
from html5.html5Attr.media import Dimensions
class Canvas( Widget,Dimensions):
	_baseClass = "canvas"

	def __init__(self, *args, **kwargs):
		super(Canvas,self).__init__( *args, **kwargs )