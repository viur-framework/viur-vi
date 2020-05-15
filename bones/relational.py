# -*- coding: utf-8 -*-
from vi import html5

from vi.priorityqueue import boneSelector
from vi.config import conf
import vi.utils as utils
from vi.bones.base import BaseBone, BaseEditWidget, BaseMultiEditWidget
from vi.widgets.internaledit import InternalEdit
from vi.widgets.list import ListWidget


def _getDefaultValues(structure):
	"""
	Gets defaultValues from a structure.
	"""
	defaultValues = {}
	for k, v in {k: v for k, v in structure}.items():
		if "params" in v.keys() and v["params"] and "defaultValue" in v["params"].keys():
			defaultValues[k] = v["params"]["defaultValue"]

	return defaultValues


class RelationalEditWidget(BaseEditWidget):
	style = ["vi-bone", "vi-bone--relational"]

	def _createWidget(self):
		return self.fromHTML(
			"""
				<ignite-input [name]="destWidget" readonly>
				<button [name]="selectBtn" class="btn--select" text="Select" icon="icons-select"></button>
			"""
		)

	def __init__(self, bone, language=None, **kwargs):
		super().__init__(bone)
		self.sinkEvent("onChange")

		self.value = None
		self.language = language

		# Current bone config
		self.formatString = self.bone.boneStructure["format"]

		# Structures
		self.destStructure = self.bone.boneStructure["relskel"]
		self.dataStructure = self.bone.boneStructure["using"]

		# Relation edit widget
		if self.dataStructure:
			self.dataWidget = InternalEdit(
				self.dataStructure,
				readOnly=self.readonly,
				defaultCat=None  # fixme: IMHO not necessary
			)
			self.appendChild(self.dataWidget)
		else:
			self.dataWidget = None

		# Current data state
		self.destKey = None

	def updateString(self):
		if not self.value:

			if self.dataWidget:
				self.dataWidget.disable()

			return

		txt = utils.formatString(
			self.formatString,
			self.value["dest"],
			self.destStructure,
			prefix=["dest"],
			language=self.language
		)

		if self.dataWidget:
			txt = utils.formatString(
				txt,
				self.dataWidget.serializeForDocument(),
				self.dataStructure,
				prefix=["rel"],
				language=self.language
			)

		self.destWidget["value"] = txt

	def onChange(self, event):
		if self.dataWidget:
			self.value["rel"] = self.dataWidget.doSave()
			self.updateString()

	def unserialize(self, value=None):
		if not value:
			self.destKey = None
			self.destWidget["value"] = ""
		else:
			self.destKey = value["dest"]["key"]

		if self.dataWidget:
			self.dataWidget.unserialize((value["rel"] or {}) if value else {})
			self.dataWidget.enable()

		self.value = value
		self.updateString()

	def serialize(self):
		# fixme: Maybe we need a serializeForDocument also?
		if self.destKey and self.dataWidget:
			res = {
				"key": self.destKey
			}
			res.update(self.dataWidget.serializeForPost())  # fixme: call serializeForPost()?
			return res

		return self.destKey or None

	def onSelectBtnClick(self):
		currentSelector = ListWidget(
			self.bone.boneStructure["module"],
			selectMode="single",
			#context=self.context
		)
		currentSelector.selectionActivatedEvent.register(self)

		conf["mainWindow"].stackWidget(currentSelector)
		self.parent().addClass("is-active")

	def onSelectionActivated(self, table, selection):
		self.unserialize({
			"dest": selection[0],
			"rel": _getDefaultValues(self.dataStructure) if self.dataStructure else None
		})


class RelationalViewWidget(html5.Div):
	style = ["vi-bone", "vi-bone--relational"]

	def __init__(self, bone, language=None, **kwargs):
		super().__init__()
		self.bone = bone
		self.language = language

		# Current bone config
		self.readonly = bool(self.bone.boneStructure.get("readonly"))
		self.formatString = self.bone.boneStructure["format"]

		# Structures
		self.destStructure = self.bone.boneStructure["relskel"]
		self.dataStructure = self.bone.boneStructure["using"]

		self.value = None

	def unserialize(self, value=None):
		self.value = value

		if value:
			txt = utils.formatString(
				self.formatString,
				value["dest"],
				self.destStructure,
				prefix=["dest"],
				language=self.language
			)

			if self.dataStructure and value["rel"]:
				txt = utils.formatString(
					txt,
					value["rel"],
					self.dataStructure,
					prefix=["rel"],
					language=self.language
				)

		else:
			txt = None

		self.appendChild(html5.TextNode(txt or conf["emptyValue"]), replace=True)

	def serialize(self):
		return self.value  # fixme: The format here is invalid for POST!


class RelationalMultiEditWidget(BaseMultiEditWidget):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.addBtn["text"] = "Select"
		self.addBtn["icon"] = "icons-select"
		self.addBtn.removeClass("btn--add")
		self.addBtn.addClass("btn--select")

	def onAddBtnClick(self):
		currentSelector = ListWidget(
			self.bone.boneStructure["module"],
			selectMode="single",
			# context=self.context
		)
		currentSelector.selectionActivatedEvent.register(self)

		conf["mainWindow"].stackWidget(currentSelector)
		self.parent().addClass("is-active")

	def onSelectionActivated(self, table, selection):
		for entry in selection:
			self.addEntry({
				"dest": entry,
				"rel": _getDefaultValues(self.bone.boneStructure["using"])
							if self.bone.boneStructure["using"] else None
			})


class RelationalBone(BaseBone):
	editWidgetFactory = RelationalEditWidget
	viewWidgetFactory = RelationalViewWidget
	multiEditWidgetFactory = RelationalMultiEditWidget

	@staticmethod
	def checkFor(moduleName, boneName, skelStructure):
		return skelStructure[boneName]["type"] == "relational" or skelStructure[boneName]["type"].startswith("relational.")


boneSelector.insert(1, RelationalBone.checkFor, RelationalBone)
