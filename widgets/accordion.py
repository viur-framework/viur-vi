# -*- coding: utf-8 -*-
from vi import html5
from vi.embedsvg import embedsvg

class AccordionSegment(html5.Fieldset):

	def __init__(self, ident, title = None):
		super(AccordionSegment, self).__init__()
		self.sinkEvent("onClick")

		self.addClass("vi-accordion-segment")
		self["name"] = ident

		legend = html5.Legend()
		legend.addClass("vi-accordion-legend")
		self.appendChild(legend)

		self.title = html5.Span()
		embedSvg = embedsvg.get("icons-arrow-right")
		if embedSvg:
			self.title.element.innerHTML = embedSvg
		self.title.appendChild(html5.TextNode(title or ident))
		self.title.addClass("vi-accordion-title")
		self.title["role"] = "button"
		legend.appendChild(self.title)

		# icon = html5.Div()
		# icon.addClass("vi-accordion-icon")
		# self.title.appendChild()

		self._section = html5.Section()
		self._section.addClass("vi-accordion-section")
		self.appendChild(self._section)

	def checkVisibility(self):
		if all([child.isHidden() for child in self._section.children()]):
			self.hide()
		else:
			self.show()

	def activate(self):
		self.addClass("is-active")

	def deactivate(self):
		self.removeClass("is-active")

	def isActive(self):
		return self.hasClass("is-active")

	def toggle(self):
		if self.isActive():
			self.deactivate()
		else:
			self.activate()

	def onClick(self, event):
		if not html5.utils.doesEventHitWidgetOrChildren(event, self.title):
			return

		for child in self.parent().children():
			if child is self:
				self.toggle()
			else:
				child.deactivate()

	def addWidget(self, widget):
		self._section.appendChild(widget)

class Accordion(html5.Form):

	def addSegment(self, ident, title = None, *args):
		seg = AccordionSegment(ident, title)
		self.appendChild(seg)
		self.addClass("vi-accordion")

		for widget in args:
			seg.addWidget(widget)

		return seg
