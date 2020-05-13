# -*- coding: utf-8 -*-
from vi import html5

from vi.priorityqueue import boneSelector
from vi.config import conf
import vi.utils as utils
from vi.bones.base import BaseBone
from vi.widgets.internaledit import InternalEdit


class RecordEditWidget(html5.Div):
	style = ["vi-bone", "vi-bone--record"]

	def __init__(self, bone, **kwargs):
		super().__init__()

		self.bone = bone
		self.value = None

		# Current bone config
		self.readonly = bool(self.bone.boneStructure.get("readonly"))

		# Relation edit widget
		self.widget = InternalEdit(
			self.bone.boneStructure["using"],
			readOnly=self.readonly,
			defaultCat=None  # fixme: IMHO not necessary
		)
		self.appendChild(self.widget)

	def unserialize(self, value=None):
		self.widget.unserialize(value or {})
		self.value = value

	def serialize(self):
		return self.widget.serializeForPost()  # fixme: call serializeForPost()?


class RecordViewWidget(html5.Div):
	style = ["vi-bone", "vi-bone--record"]

	def __init__(self, bone, language=None, **kwargs):
		super().__init__()
		self.bone = bone
		self.language = language

		# Current bone config
		self.readonly = bool(self.bone.boneStructure.get("readonly"))
		self.formatString = self.bone.boneStructure["format"]

		# Structures
		self.structure = self.bone.boneStructure["using"]

		self.value = None

	def unserialize(self, value=None):
		self.value = value

		if value:
			txt = utils.formatString(
				self.formatString,
				value,
				self.structure,
				language=self.language
			)

		else:
			txt = None

		self.appendChild(html5.TextNode(txt or conf["emptyValue"]), replace=True)

	def serialize(self):
		return self.value  # fixme: The format here is invalid for POST!


class RecordBone(BaseBone):
	editWidgetFactory = RecordEditWidget
	viewWidgetFactory = RecordViewWidget

	@staticmethod
	def checkFor(moduleName, boneName, skelStructure):
		return skelStructure[boneName]["type"] == "record" or skelStructure[boneName]["type"].startswith("record.")


boneSelector.insert(1, RecordBone.checkFor, RecordBone)
