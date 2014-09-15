from html5.widget import Widget
from html5.html5Attr.media import Media

class Style( Widget,Media ):
	_baseClass = "style"

	def __init__(self, *args, **kwargs):
		super(Style,self).__init__( *args, **kwargs )
	def _getScoped(self):
		return( True if self.element.hasAttribute("scoped") else False )
	def _setScoped(self,val):
		if val==True:
			self.element.setAttribute("scoped","")
		else:
			self.element.removeAttribute("scoped")
