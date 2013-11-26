import html5

class ToolTip(html5.A):
	"""
		Small utility class for providing tooltips
	"""
	__toolTipIdx_ = 0 #Internal counter to ensure unique ids

	def __init__(self, shortText="popup", longText="", *args, **kwargs):
		super( ToolTip, self ).__init__( *args, **kwargs )
		self["class"] = "tooltip"
		self.toolTipIdx = ToolTip.__toolTipIdx_
		self.toolTipIdx += 1
		self.appendChild(html5.TextNode(shortText))
		self["href"] = "#tooltip_contents_%s" % self.toolTipIdx
		span = html5.Span()
		span.element.innerHTML = longText
		span["id"] = "#tooltip_contents_%s" % self.toolTipIdx
		self.appendChild( span )

