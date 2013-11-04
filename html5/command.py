from html5.widget import Widget

class Command( Widget):
	_baseClass = "command"

	def __init__(self, *args, **kwargs):
		super(Command,self).__init__( *args, **kwargs )

	def _getChecked(self):
		return( True if self.element.hasAttribute("checked") else False )
	def _setChecked(self,val):
		if val==True:
			self.element.setAttribute("checked","")
		else:
			self.element.removeAttribute("checked")

	def _getDisabled(self):
		return( True if self.element.hasAttribute("disabled") else False )
	def _setDisabled(self,val):
		if val==True:
			self.element.setAttribute("disabled","")
		else:
			self.element.removeAttribute("disabled")

	def _getIcon(self):
		return self.element.icon
	def _setIcon(self,val):
		self.element.icon=val

	def _getLabel(self):
		return self.element.label
	def _setLabel(self,val):
		self.element.label=val

	def _getRadiogroup(self):
		return self.element.radiogroup
	def _setRadiogroup(self,val):
		self.element.radiogroup=val

	def _getType(self):
		return self.element.type
	def _setType(self,val):
		self.element.type=val