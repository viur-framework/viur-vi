from html5.form import Button as fButton

class Button(fButton):
	def __init__(self, txt=None, callback=None, *args, **kwargs):
		super(Button,self).__init__(*args, **kwargs)
		self["class"] = "button"
		if txt is not None:
			self.element.innerHTML = txt
		self.callback = callback
		self.sinkEvent("onClick")

	def onClick(self, event):
		event.stopPropagation()
		event.preventDefault()
		if self.callback is not None:
			self.callback(self)

	def onDetach(self):
		super(Button,self)
		self.callback = None
