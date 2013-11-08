from html5.widget import Widget
from html5.html5Attr.cite import Cite,Datetime
class _Del( Widget,Cite,Datetime):
	_baseClass = "_del"

	def __init__(self, *args, **kwargs):
		super(_Del,self).__init__( *args, **kwargs )