from flare import html5, utils
from flare.icons import SvgIcon


class AccordionSegment(html5.Fieldset):

	def __init__(self, ident, title=None):
		super(AccordionSegment, self).__init__()
		self.sinkEvent("onClick")

		self.addClass("vi-accordion-segment")
		self["name"] = ident

		legend = html5.Legend()
		legend.addClass("vi-accordion-legend")
		self.appendChild(legend)

		self.title = html5.Span()
		self.title.prependChild(SvgIcon("icon-arrow-right", title=title))
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
		if not utils.doesEventHitWidgetOrChildren(event, self.title):
			return
		# event.stopPropagation()
		event.preventDefault()

		for child in self.parent().children():
			if child is self:
				self.toggle()
			else:
				child.deactivate()

	def addWidget(self, widget):
		self._section.appendChild(widget)


class Accordion(html5.Form):

	def __init__(self):
		super().__init__()
		self._segments = []

	def addSegment(self, ident, title=None, directAdd=False, *args):
		seg = AccordionSegment(ident, title)
		if directAdd:
			self.appendChild(seg)  # used for editviews
		else:
			self._segments.append(seg)  # normal form Cats can be ordered
		self.addClass("vi-accordion")

		for widget in args:
			seg.addWidget(widget)

		return seg

	def clear(self):
		self._segments.clear()
		self.removeAllChildren()

	def buildAccordion(self, order=None):
		'''

		:param sort: None: sorted by Bones, "asc":ascending, "desc":descending, dict: {"category":index,...}
		:return:
		'''
		if order == "asc":
			self._segments.sort(key=lambda x: x["name"])
		elif order == "desc":
			self._segments.sort(key=lambda x: x["name"], reverse=True)
		elif isinstance(order, list):
			self._segments.sort(key=lambda x: order.index(x["name"]) if x["name"] in order else 999)

		for s in self._segments:
			self.appendChild(s)

		self._segments.clear()  # reset all added sections
