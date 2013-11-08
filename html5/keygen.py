from html5.widget import Widget

class Keygen( Widget ):
    _baseClass = "keygen"

    def __init__(self, *args, **kwargs):
        super(Keygen,self).__init__( *args, **kwargs )

	def _getDisabled(self):
		return( True if self.element.hasAttribute("disabled") else False )
	def _setDisabled(self,val):
		if val==True:
			self.element.setAttribute("disabled","")
		else:
			self.element.removeAttribute("disabled")

	def _getName(self):
		return self.element.name
	def _setName(self,val):
		self.element.name=val

	def _getAutofocus(self):
		return( True if self.element.hasAttribute("autofocus") else False )
	def _setAutofocus(self,val):
		if val==True:
			self.element.setAttribute("autofocus","")
		else:
			self.element.removeAttribute("autofocus")

	def _getChallenge(self):
		return( True if self.element.hasAttribute("challenge") else False )
	def _setChallenge(self,val):
		if val==True:
			self.element.setAttribute("challenge","")
		else:
			self.element.removeAttribute("challenge")

	def _getForm(self):
		return self.element.form
	def _setForm(self,val):
		self.element.form=val

	def _getKeytype(self):
		return self.element.keytype
	def _setKeytype(self,val):
		self.element.keytype=val
