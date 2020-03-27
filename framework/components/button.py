from ... import html5
from ...embedsvg import embedsvg

class Button(html5.ext.Button):
	def __init__(self, txt=None, callback=None, className=None, icon = None, *args, **kwargs):
		super(Button, self).__init__(txt=txt, callback=callback, className=className, *args, **kwargs)
		self.svg = None
		if icon:
			svg = embedsvg.get(icon)
			self.svg = svg
			if svg:
				self.element.innerHTML = svg + self.element.innerHTML


	def setText(self, txt):
		if txt is not None:
			if "svg" in dir(self) and self.svg:
				self.element.innerHTML = self.svg + txt
			else:
				self.element.innerHTML = txt
			self["title"] = txt
		else:
			self.element.innerHTML = ""
			self["title"] = ""
