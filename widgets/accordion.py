# -*- coding: utf-8 -*-
import html5

class AccordionSegment(html5.Fieldset):

	def __init__(self, ident, title = None):
		super(AccordionSegment, self).__init__()
		self.sinkEvent("onClick")

		self.addClass("inactive")
		self["name"] = ident

		legend = html5.Legend()
		self.appendChild(legend)

		self.title = html5.A()
		self.title.appendChild(html5.TextNode(title or ident))
		legend.appendChild(self.title)

		self._section = html5.Section()
		self.appendChild(section)

	def checkVisibility(self):
		if all([child.isHidden() for child in self._section.children()]):
			self.hide()
		else:
			self.show()

	def activate(self):
		self.removeClass("inactive")
		self.addClass("active")

	def deactivate(self):
		self.removeClass("active")
		self.addClass("inactive")

	def isActive(self):
		return "inactive" not in self["class"]

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

		for widget in args:
			seg.addWidget(widget)

		return seg
