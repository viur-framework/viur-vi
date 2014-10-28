from html5.base import Base
from html5.html5Attr.href import Href
from html5.html5Attr.media import Media
from html5.html5Attr.rel import Rel
from html5.html5Attr.form import Name

class A( Base, Href, Media, Rel, Name ):
	_baseClass = "a"

	def __init__(self, *args, **kwargs):
		super(A,self).__init__( *args, **kwargs )

	def _getDownload(self):
		"""
		The download attribute specifies the path to a download
		@return: filename
		"""
		return self.element.download

	def _setDownload(self,val):
		"""
		The download attribute specifies the path to a download
		@param val: filename
		"""
		self.element.download = val






