# -*- coding: utf-8 -*-
from vi import html5
from vi.config import conf
from vi.priorityqueue import boneSelector
from vi.bones.base import BaseBone, BaseEditWidget, BaseViewWidget
from vi.widgets.htmleditor import HtmlEditor


class TextEditWidget(BaseEditWidget):
	style = ["vi-bone", "vi-bone--text"]

	def __init__(self, bone, **kwargs):
		super().__init__(bone, **kwargs)

	def _createWidget(self):
		if self.bone.boneStructure["validHtml"]:
			self.widget = HtmlEditor()
			self.widget.boneName = self.bone.boneName  # fixme WTF?

			if bool(self.bone.boneStructure.get("readonly")):
				self.widget.disable()
		else:
			self.widget = html5.ignite.Textarea()
			self.widget["readonly"] = bool(self.bone.boneStructure.get("readonly"))

		self.appendChild(self.widget)
		self.sinkEvent("onKeyUp")

		#self.changeEvent = EventDispatcher("boneChange")  # fixme: later...

	def _setDisabled(self, disable):
		super()._setDisabled(disable)

		if not disable and not self._disabledState and self.parent() and self.parent().hasClass("is-active"):
			self.parent().removeClass("is-active")


class TextViewWidget(BaseViewWidget):

	def unserialize(self, value=None):
		self.value = value
		self.appendChild(value or conf["emptyValue"], replace=True)


class TextBone(BaseBone):
	editWidgetFactory = TextEditWidget
	viewWidgetFactory = TextViewWidget

	@staticmethod
	def checkFor(moduleName, boneName, skelStructure):
		print(boneName, skelStructure[boneName]["type"] == "text" or skelStructure[boneName]["type"].startswith("text."))

		return skelStructure[boneName]["type"] == "text" or skelStructure[boneName]["type"].startswith("text.")


boneSelector.insert(1, TextBone.checkFor, TextBone)
