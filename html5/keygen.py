from html5.widget import Widget
from html5.html5Attr.form import _Form as Form,Autofocus,Disabled
class Keygen( Widget,Form,Autofocus,Disabled):
	_baseClass = "keygen"

	def __init__(self, *args, **kwargs):
		super(Keygen,self).__init__( *args, **kwargs )

	def _getChallenge(self):
		return( True if self.element.hasAttribute("challenge") else False )
	def _setChallenge(self,val):
		if val==True:
			self.element.setAttribute("challenge","")
		else:
			self.element.removeAttribute("challenge")

	def _getKeytype(self):
		return self.element.keytype
	def _setKeytype(self,val):
		self.element.keytype=val
