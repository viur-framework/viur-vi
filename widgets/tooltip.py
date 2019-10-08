# -*- coding: utf-8 -*-
from vi import html5
from vi.i18n import translate
from vi.framework.embedsvg import embedsvg


class ToolTip(html5.Div):
	"""
		Small utility class for providing tooltips
	"""

	def __init__(self, shortText="", longText="", *args, **kwargs):
		super( ToolTip, self ).__init__( *args, **kwargs )
		self["class"] = "vi-tooltip msg is-active"
		self.sinkEvent("onClick")
		svg = embedsvg.get("icons-arrow-right")
		if svg:
			self.element.innerHTML = svg

		self.fromHTML("""
			<div class="msg-content" [name]="tooltipMsg">
				<h2 class="msg-headline" [name]="tooltipHeadline"></h2>
				<div class="msg-descr" [name]="tooltipDescr"></div>
			</div>
		""")

		self.tooltipHeadline.element.innerHTML = translate("vi.tooltip.headline") + " " + shortText
		self.tooltipDescr.element.innerHTML = longText.replace( "\n", "<br />" )

	def onClick(self, event):
		self.toggleClass("is-open")

	def _setDisabled(self, disabled):
		return

	def _getDisabled(self):
		return False
