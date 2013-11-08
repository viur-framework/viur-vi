from html5.widget import Widget
from html5.html5Attr.href import Href,Target

class Base( Widget,Href ,Target):
	_baseClass = "base"

	def __init__(self, *args, **kwargs):
		super(Base,self).__init__( *args, **kwargs )

