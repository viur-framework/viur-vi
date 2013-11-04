from html5.widget import Widget

class Del( Widget):
	_baseClass = "del"

	def __init__(self, *args, **kwargs):
		super(Del,self).__init__( *args, **kwargs )

	def _getCite(self):
		return self.element.cite
	def _setCite(self,val):
		self.element.cite=val

	def _getDatetime(self):
		return self.element.datetime
	def _setDatetime(self,val):
		self.element.datetime=val