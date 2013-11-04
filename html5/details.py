from html5.widget import Widget

class Details( Widget):
	_baseClass = "details"

	def __init__(self, *args, **kwargs):
		super(Details,self).__init__( *args, **kwargs )


	def _getOpen(self):
		return( True if self.element.hasAttribute("open") else False )
	def _setOpen(self,val):
		if val==True:
			self.element.setAttribute("open","")
		else:
			self.element.removeAttribute("open")