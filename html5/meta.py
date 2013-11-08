from html5.widget import Widget

class Meta( Widget ):
    _baseClass = "meta"

    def __init__(self, *args, **kwargs):
        super(Meta,self).__init__( *args, **kwargs )

	def _getName(self):
		return self.element.name
	def _setName(self,val):
		self.element.name=val

	def _getCharset(self):
		return self.element.charset
	def _setCharset(self,val):
		self.element.charset=val

	def _getContent(self):
		return self.element.content
	def _setContent(self,val):
		self.element.content=val

	'''
	def _getHttpequiv(self):
		return self.element.http-equiv
	def _setHttpequiv(self,val):
		self.element.http-equiv=val
	'''

