from html5.widget import Widget
from html5.html5Attr.form import Name
from html5.html5Attr.charset import Charset

class Meta( Widget,Name,Charset ):
	_baseClass = "meta"

	def __init__(self, *args, **kwargs):
		super(Meta,self).__init__( *args, **kwargs )

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

