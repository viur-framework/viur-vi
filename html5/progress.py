from html5.widget import Widget
from html5.html5Attr.form import Value
class Progress( Widget,Value ):
	_baseClass = "progress"

	def __init__(self, *args, **kwargs):
		super(Progress,self).__init__( *args, **kwargs )

	def _getMax(self):
		return self.element.max

	def _setMax(self,val):
		self.element.max=val




