import html5

class ToolTip(html5.Div):
	"""
		Small utility class for providing tooltips
	"""
	__toolTipIdx_ = 0 #Internal counter to ensure unique ids

	def __init__(self, shortText="Tooltip", longText="", *args, **kwargs):
		super( ToolTip, self ).__init__( *args, **kwargs )
		self["class"] = "tooltip"
		self.toolTipIdx = ToolTip.__toolTipIdx_
		self.toolTipIdx += 1
		a = html5.A()
		a.appendChild(html5.TextNode(shortText))
		a["href"] = "#tooltip_contents_%s" % self.toolTipIdx
		self.appendChild(a)
		span = html5.Span()
		span.element.innerHTML = longText
		span["id"] = "#tooltip_contents_%s" % self.toolTipIdx
		self.appendChild( span )

