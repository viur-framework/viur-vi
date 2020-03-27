# -*- coding: utf-8 -*-
from vi.embedsvg import embedsvg
from vi import html5

class Icon(html5.Div):
	'''
		Wrapper to load embedevgs or imgs. With fallback for broken IMGs
	'''
	def __init__(self, descr, icon=None):
		super(Icon, self).__init__()
		self._icon = icon
		self._descr = descr

		self.addClass("item-image")

		self.modulIcon = html5.I()
		self.modulIcon.addClass("i")

		if icon:
			embedSvg = embedsvg.get(self._icon)

			if embedSvg:
				self.modulIcon.element.innerHTML = embedSvg + self.modulIcon.element.innerHTML
				self.appendChild(self.modulIcon)

			else:
				img = html5.Img()
				img.onError = lambda e: self.onError(e)
				img.sinkEvent("onError")
				img["src"] = self._icon
				self.modulIcon.appendChild(img)

		else:
			self.modulIcon.appendChild(self._descr[:1])

		self.appendChild(self.modulIcon)

	def onError(self, event):
		self.modulIcon.removeAllChildren()
		self.modulIcon.appendChild(self._descr[:1])





