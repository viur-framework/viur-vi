import html5

class ToolTip(html5.Div):
	"""
		Small utility class for providing tooltips
	"""

	def __init__(self, shortText="Tooltip", longText="", *args, **kwargs):
		super( ToolTip, self ).__init__( *args, **kwargs )
		self["class"] = "vi-tooltip msg is-active"

		tooltipToggleBtn = html5.ext.Button(shortText, self.toggleTooltip )
		self.appendChild(tooltipToggleBtn)

		tooltipHeadline = html5.H2()
		tooltipHeadline.addClass("msg-headline")
		tooltipHeadline.element.innerHTML = shortText
		self.appendChild(tooltipHeadline)

		tooltipMsg = html5.Div()
		tooltipMsg.addClass("msg-content")
		tooltipMsg.element.innerHTML = longText.replace( "\n", "<br />" )
		self.appendChild(tooltipMsg)

	def toggleTooltip(self, *args, **kwargs):
		self.toggleClass("is-open")

	def _setDisabled(self, disabled):
		return

	def _getDisabled(self):
		return False
