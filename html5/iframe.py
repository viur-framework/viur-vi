from html5.widget import Widget
from html5.html5Attr.src import Src
from html5.html5Attr.form import Name
from html5.html5Attr.media import Dimensions
class Iframe( Widget,Src,Name,Dimensions):
	_baseClass = "iframe"

	def __init__(self, *args, **kwargs):
		super(Iframe,self).__init__( *args, **kwargs )

	def _getSandbox(self):
		return self.element.sandbox

	def _setSandbox(self,val):
		self.element.sandbox=val

	def _getSrcdoc(self):
		return self.element.src
	def _setSrcdoc(self,val):
		self.element.src=val

	def _getSeamless(self):
		return( True if self.element.hasAttribute("seamless") else False )
	def _setSeamless(self,val):
		if val==True:
			self.element.setAttribute("seamless","")
		else:
			self.element.removeAttribute("seamless")