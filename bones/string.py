from vi import html5

from vi.priorityqueue import boneSelector
from vi.config import conf
from vi.bones.base import BaseBone, BaseEditWidget, BaseViewWidget


class StringEditWidget(BaseEditWidget):
	style = ["vi-value", "vi-value--string", "input-group"]

	def createWidget(self):
		# language=HTML
		self.appendChild("""
			<ignite-input [name]="widget">
			<div class="label" [name]="length" hidden>0</div> <!-- fixme: add later ... -->
			<div class="label" [name]="maxlength" hidden>0</div> <!-- fixme: add later ... -->
		""")

		self.sinkEvent("onChange", "onKeyUp")
		self.timeout = None

	def onChange(self, event):
		if self.timeout:
			html5.window.clearTimeout(self.timeout)

		self.renderTimeout()

	def onKeyUp(self, event):
		if self.timeout:
			html5.window.clearTimeout(self.timeout)

		self.timeout = html5.window.setTimeout(self.renderTimeout, 125)
		event.stopPropagation()

	def renderTimeout(self):
		self.timeout = None
		self.updateLength()

	def updateLength(self):
		self.length.appendChild(len(self.widget["value"] or ""), replace=True)

	def unserialize(self, value=None):
		self.widget["value"] = html5.utils.unescape(str(value or ""))  # fixme: is html5.utils.unescape() still required?
		self.updateLength()

	def serialize(self):
		return self.widget["value"]


class StringViewWidget(BaseViewWidget):
	# fixme: Do we really need this? BaseViewWidget should satisfy,
	#           the call to html5.utils.unescape() is the only difference.

	def unserialize(self, value=None):
		self.value = value
		self.appendChild(html5.TextNode(html5.utils.unescape(value or conf["emptyValue"])), replace=True)


class StringBone(BaseBone):
	editWidgetFactory = StringEditWidget
	viewWidgetFactory = StringViewWidget

	@staticmethod
	def checkFor(moduleName, boneName, skelStructure):
		return skelStructure[boneName]["type"] == "str" or skelStructure[boneName]["type"].startswith("str.")


boneSelector.insert(1, StringBone.checkFor, StringBone)

