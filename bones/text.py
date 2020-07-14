# -*- coding: utf-8 -*-
from vi import html5
from vi.config import conf
from vi.priorityqueue import boneSelector
from vi.bones.base import BaseBone, BaseEditWidget, BaseViewWidget
from vi.widgets.htmleditor import HtmlEditor


class TextEditWidget(BaseEditWidget):
	style = ["vi-value", "vi-value--text"]

	def createWidget(self):
		if self.bone.boneStructure["validHtml"]:
			widget = HtmlEditor()
			widget.boneName = self.bone.boneName  # fixme WTF?

			if bool(self.bone.boneStructure.get("readonly")):
				widget.disable()
		else:
			widget = html5.ignite.Textarea()
			widget["readonly"] = bool(self.bone.boneStructure.get("readonly"))

		self.sinkEvent("onKeyUp")

		#self.changeEvent = EventDispatcher("boneChange")  # fixme: later...
		return widget

	def updateWidget(self):
		if self.bone.readonly:
			if isinstance(self.widget, HtmlEditor):
				self.widget.disable()
			else:
				self.widget["readonly"] = True
		else:
			if isinstance(self.widget, HtmlEditor):
				self.widget.enable()
			else:
				self.widget["readonly"] = False

		# fixme: required?

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
		return skelStructure[boneName]["type"] == "text" or skelStructure[boneName]["type"].startswith("text.")


boneSelector.insert(1, TextBone.checkFor, TextBone)
