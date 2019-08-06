import html5
from vi.embedsvg import embedsvg


class Button(html5.ext.Button):
	def __init__(self, txt=None, callback=None, className=None, icon = None, *args, **kwargs):
		super(Button, self).__init__(txt=txt, callback=callback, className=className, *args, **kwargs)

		if icon:
			svg = embedsvg.get(icon)
			if svg:
				self.element.innerHTML = svg + self.element.innerHTML
