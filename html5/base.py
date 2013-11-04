from html5.widget import Widget

class Base( Widget ):
	_baseClass = "base"

	def __init__(self, *args, **kwargs):
		super(Base,self).__init__( *args, **kwargs )



	def _getHref(self):
		"""
		Url of a Page
		@param self:
		"""
		return self.element.href

	def _setHref(self, val):
		"""
		Url of a Page
		@param val:
		"""
		self.element.href=val

	def _getTarget(self):
		return self.element.target
	def _setTarget(self,val):
		self.element.target=val