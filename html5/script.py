from html5.widget import Widget

class Script( Widget ):
    _baseClass = "script"

    def __init__(self, *args, **kwargs):
        super(Script,self).__init__( *args, **kwargs )

	def _getAsync(self):
		return( True if self.element.hasAttribute("async") else False )
	def _setAsync(self,val):
		if val==True:
			self.element.setAttribute("async","")
		else:
			self.element.removeAttribute("async")

	def _getCharset(self):
		return self.element.charset
	def _setCharset(self,val):
		self.element.charset=val

	def _getDefer(self):
		return( True if self.element.hasAttribute("defer") else False )
	def _setDefer(self,val):
		if val==True:
			self.element.setAttribute("defer","")
		else:
			self.element.removeAttribute("defer")

	def _getSrc(self):
		return self.element.src
	def _setSrc(self,val):
		self.element.src=val

	def _getType(self):
		return self.element.type
	def _setType(self,val):
		self.element.type=val




