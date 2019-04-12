# -*- coding: utf-8 -*-
import html5

class ToolTip(html5.Div):
	"""
		Small utility class for providing tooltips
	"""

	def __init__(self, shortText="Tooltip", longText="", *args, **kwargs):
		super( ToolTip, self ).__init__( *args, **kwargs )
		self["class"] = "tooltip"
		a = html5.ext.Button(shortText, self.toggleMsgCenter )
		a.appendChild(html5.TextNode())
		#a["href"] = "#tooltip_contents_%s" % self.toolTipIdx
		self.appendChild(a)
		span = html5.Span()
		span.element.innerHTML = longText.replace( "\n", "<br />" )
		self.appendChild( span )

	def toggleMsgCenter(self, *args, **kwargs):
		self.toggleClass("is_open")

	def _setDisabled(self, disabled):
		return

	def _getDisabled(self):
		return False
