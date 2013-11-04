from html5.widget import Widget

class Audio( Widget ):
	_baseClass = "audio"

	def __init__(self, *args, **kwargs):
		super(Audio,self).__init__( *args, **kwargs )

	def _getAutoplay(self):
		return( True if self.element.hasAttribute("autoplay") else False )
	def _setAutoplay(self,val):
		if val==True:
			self.element.setAttribute("autoplay","")
		else:
			self.element.removeAttribute("autoplay")

	def _getControls(self):
		return( True if self.element.hasAttribute("controls") else False )
	def _setControls(self,val):
		if val==True:
			self.element.setAttribute("controls","")
		else:
			self.element.removeAttribute("controls")

	def _getLoop(self):
		return( True if self.element.hasAttribute("loop") else False )
	def _setLoop(self,val):
		if val==True:
			self.element.setAttribute("loop","")
		else:
			self.element.removeAttribute("loop")

	def _getMuted(self):
		return( True if self.element.hasAttribute("muted") else False )
	def _setMuted(self,val):
		if val==True:
			self.element.setAttribute("muted","")
		else:
			self.element.removeAttribute("muted")

	def _getPreload(self):
		return self.element.preload
	def _setPreload(self,val):
		self.element.preload=val

	def _getSrc(self):
		return self.element.src
	def _setSrc(self,val):
		self.element.src=val

