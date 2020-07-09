from ... import html5
from ...embedsvg import embedsvg

class Button(html5.ext.Button):
	showtxt = True
	def __init__(self, txt=None, callback=None, className=None, icon = None, *args, **kwargs):
		super(Button, self).__init__(txt=txt, callback=callback, className=className, *args, **kwargs)
		self.svg = None
		if "notext" in kwargs and kwargs["notext"]:
			self.showtxt = False
			self.addClass("btn-texthidden")
		else:
			self.showtxt = True

		if icon:
			svg = embedsvg.get(icon)
			self.svg = svg
			if svg:
				self.element.innerHTML = svg + (self.element.innerHTML if self.showtxt else "")


	def resetIcon( self ):
		title = ""
		if self.showtxt:
			title = self["title"]

		if self.svg:
			self.element.innerHTML = self.svg + title
		else:
			self.element.innerHTML = title

	def setIcon( self,icon ):
		if not icon:
			return 0

		title = ""
		if self.showtxt:
			title = self[ "title" ]

		svg = embedsvg.get( icon )
		if svg:
			self.element.innerHTML = svg + title

	def setText(self, txt):
		if txt is not None:
			if self.showtxt:
				if "svg" in dir(self) and self.svg:
					self.element.innerHTML = self.svg + txt
				else:
					self.element.innerHTML = txt

			self["title"] = txt
		else:
			self.element.innerHTML = ""
			self["title"] = ""
