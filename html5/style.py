from html5.widget import Widget

class Style( Widget ):
    _baseClass = "style"

    def __init__(self, *args, **kwargs):
        super(Style,self).__init__( *args, **kwargs )

	def _getMedia(self):
		return self.element.media
	def _setMedia(self,val):
		self.element.media=val

	def _getScoped(self):
		return( True if self.element.hasAttribute("scoped") else False )
	def _setScoped(self,val):
		if val==True:
			self.element.setAttribute("scoped","")
		else:
			self.element.removeAttribute("scoped")

	def _getType(self):
		return self.element.type
	def _setType(self,val):
		self.element.type=val