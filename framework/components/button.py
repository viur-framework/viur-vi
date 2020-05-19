from ... import html5
from ...embedsvg import embedsvg
from ...i18n import translate

@html5.tag
class Button(html5.Button):
	def __init__(self, text=None, callback=None, className="", icon=None):
		super(Button, self).__init__()
		self.addClass("btn", className)
		self.sinkEvent("onClick")
		self.svg = None

		if icon is not None:
			self["icon"] = icon

		if text is not None:
			self["text"] = text

		self.callback = callback

	def onBind(self, widget, name):
		if self.callback is None:
			funcName = "on" + name[0].upper() + name[1:] + "Click"
			if funcName in dir(widget):
				self.callback = getattr(widget, funcName)

	def onClick(self, event):
		event.stopPropagation()
		event.preventDefault()

		if self.callback is not None:
			try:
				self.callback(self)
			except:
				self.callback()

	def resetIcon(self):
		if self.svg:
			self.element.innerHTML = self.svg + self["title"]
		else:
			self.element.innerHTML = self["title"]

	def _setIcon(self, icon):
		if not icon:
			return

		svg = embedsvg.get(icon)
		if svg:
			self.svg = svg
			self.element.innerHTML = self.svg + self["title"]

	def _setText(self, text):
		if text is not None:
			self.element.innerHTML = (self.svg or "") + translate(text)
			self["title"] = text
		else:
			self.element.innerHTML = ""
			self["title"] = ""
