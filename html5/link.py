from html5.widget import Widget

class Link( Widget ):
    _baseClass = "link"

    def __init__(self, *args, **kwargs):
        super(Link,self).__init__( *args, **kwargs )

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

	def _getSizes(self):
		return self.element.sizes
	def _setSizes(self,val):
		self.element.sizes=val



