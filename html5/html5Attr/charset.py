class Charset(object):
	def _getCharset(self):
		return self.element.charset
	def _setCharset(self,val):
		self.element.charset=val