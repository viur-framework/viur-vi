from vi import html5

from vi.priorityqueue import boneSelector
from vi.config import conf
from vi.bones.base import BaseBone, BaseEditWidget, BaseViewWidget
from vi.i18n import translate


class BooleanEditWidget(BaseEditWidget):
	style = ["vi-value", "vi-value--boolean"]

	def createWidget(self):
		return html5.ignite.Switch()

	def updateWidget(self):
		if self.bone.readonly:
			self.widget.disable()
		else:
			self.widget.enable()

	def unserialize(self, value=None):
		self.widget["checked"] = bool(value)

	def serialize(self):
		return self.widget["checked"]


class BooleanViewWidget(BaseViewWidget):

	def unserialize(self, value=None):
		self.value = value
		self.appendChild(html5.TextNode(translate(str(bool(value)))), replace=True)


class BooleanBone(BaseBone):
	editWidgetFactory = BooleanEditWidget
	viewWidgetFactory = BooleanViewWidget
	multiEditWidgetFactory = None
	multiViewWidgetFactory = None

	@staticmethod
	def checkFor(moduleName, boneName, skelStructure):
		return skelStructure[boneName]["type"] == "bool" or skelStructure[boneName]["type"].startswith("bool.")


boneSelector.insert(1, BooleanBone.checkFor, BooleanBone)
