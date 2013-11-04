from html5.base import Base

class A( Base ):
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

	def _getHreflang(self):
		return self.element.hreflang
	def _setHreflang(self,val):
		self.element.hreflang=val
	def _getMedia(self):
		return self.element.media
	def _setMedia(self,val):
		self.element.media=val
	def _getRel(self):
		return self.element.rel
	def _setRel(self,val):
		self.element.rel=val
	def _getType(self):
		return self.element.type
	def _setType(self,val):
		self.element.type=val





