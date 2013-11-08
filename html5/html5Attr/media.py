class Type(object):
	def _getType(self):
		return self.element.type
	def _setType(self,val):
		self.element.type=val

class Media(Type):
	def _getMedia(self):
		return self.element.media
	def _setMedia(self,val):
		self.element.media=val

class Dimensions(object):
	def _getWidth(self):
		return self.element.width
	def _setWidth(self,val):
		self.element.width=val

	def _getHeight(self):
		return self.element.height
	def _setHeight(self,val):
		self.element.height=val

class Usemap(object):
	def _getUsemap(self):
		return self.element.usemap
	def _setUsemap(self,val):
		self.element.usemap=val

class Multimedia(object):
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