class Href(object):
	def _getHref(self):
		"""
		Url of a Page
		@param self:
		"""
		return self.element.href

	def _setHref(self, val):
		"""
		Url of a Page
		@param val: URL
		"""
		self.element.href=val

	def _getHreflang(self):
		return self.element.hreflang
	def _setHreflang(self,val):
		self.element.hreflang=val

class Target(object):
	def _getTarget(self):
		return self.element.target
	def _setTarget(self,val):
		self.element.target=val