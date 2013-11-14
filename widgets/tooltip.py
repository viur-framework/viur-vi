import html5

class ToolTip(html5.A):
	def __init__(self, shortText="popup", longText="", *args, **kwargs):
		super( ToolTip, self ).__init__( *args, **kwargs )
		self["class"] = "tooltip"
		self.appendChild(html5.TextNode(shortText))
		span = html5.Span()
		span.element.innerHTML = longText
		self.appendChild( span )

