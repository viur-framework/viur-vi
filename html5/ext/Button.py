from html5.a import A

class Button(A):
	def __init__(self, txt=None, callback=None, *args, **kwargs):
		super(Button,self).__init__(*args, **kwargs)
		self["class"] = "button"
		if txt is not None:
			self.element.innerHTML = txt
		self.callback = callback
		self.sinkEvent("onClick")

	def onClick(self, event):
		event.stopPropagation()
		if self.callback is not None:
			self.callback()

	def onDetach(self):
		super(Button,self)
		self.callback = None
