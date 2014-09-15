from html5.widget import Widget
from html5.html5Attr.src import Src
from html5.html5Attr.charset import Charset

class _Script( Widget,Src,Charset ):
	_baseClass = "script"

	def __init__(self, *args, **kwargs):
		super(_Script,self).__init__( *args, **kwargs )

	def _getAsync(self):
		return( True if self.element.hasAttribute("async") else False )
	def _setAsync(self,val):
		if val==True:
			self.element.setAttribute("async","")
		else:
			self.element.removeAttribute("async")

	def _getDefer(self):
		return( True if self.element.hasAttribute("defer") else False )
	def _setDefer(self,val):
		if val==True:
			self.element.setAttribute("defer","")
		else:
			self.element.removeAttribute("defer")




