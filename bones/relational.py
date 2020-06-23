# -*- coding: utf-8 -*-
from vi import html5, utils

from vi.priorityqueue import boneSelector, moduleWidgetSelector
from vi.config import conf
from vi.bones.base import BaseBone, BaseEditWidget, BaseMultiEditWidget
from vi.widgets.internaledit import InternalEdit
from vi.widgets.tree import TreeNodeWidget, TreeLeafWidget
from vi.widgets.file import FileWidget, Uploader, FilePreviewImage


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
				<button hidden [name]="deleteBtn" class="btn--delete" text="Delete" icon="icons-delete"></button>
			"""
		)

	def _updateWidget(self):
		super()._updateWidget()

		if self.bone.readonly:
			self.selectBtn.hide()
			self.deleteBtn.hide()
		else:
			self.selectBtn.show()

			# Only allow to delete entry when not multiple and not required!
			if not self.bone.multiple and not self.bone.required:
				self.deleteBtn.show()

	def __init__(self, bone, language=None, **kwargs):
		super().__init__(bone)
		self.sinkEvent("onChange")

		self.value = None
		self.language = language

		# Relation edit widget
		if self.bone.dataStructure:
			self.dataWidget = InternalEdit(
				self.bone.dataStructure,
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
			self.bone.formatString,
			self.value["dest"],
			self.bone.destStructure,
			prefix=["dest"],
			language=self.language
		)

		if self.dataWidget:
			txt = utils.formatString(
				txt,
				self.dataWidget.serializeForDocument(),
				self.bone.dataStructure,
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
		selector = conf["selectors"].get(self.bone.destModule)

		if selector is None:
			selector = moduleWidgetSelector.select(self.bone.destModule, self.bone.destInfo)
			assert selector, "No selector can be found for %r" % self.destModule

			selector = selector(
				self.bone.destModule,
				**self.bone.destInfo
			)

			conf["selectors"][self.bone.destModule] = selector

		# todo: set context

		# Start widget with selector callback
		selector.setSelector(
			lambda selector, selection: self.unserialize({
				"dest": selection[0],
				"rel": _getDefaultValues(self.bone.dataStructure) if self.bone.dataStructure else None
			}),
			multi=self.bone.multiple,
			allow=self.bone.selectorAllow
		)

	def onDeleteBtnClick(self):
		self.unserialize()


class RelationalViewWidget(html5.Div):
	style = ["vi-bone", "vi-bone--relational"]

	def __init__(self, bone, language=None, **kwargs):
		super().__init__()
		self.bone = bone
		self.language = language
		self.value = None

	def unserialize(self, value=None):
		self.value = value

		if value:
			txt = utils.formatString(
				self.bone.formatString,
				value["dest"],
				self.bone.destStructure,
				prefix=["dest"],
				language=self.language
			)

			if self.bone.dataStructure and value["rel"]:
				txt = utils.formatString(
					txt,
					value["rel"],
					self.bone.dataStructure,
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
		selector = conf["selectors"].get(self.bone.destModule)

		if selector is None:
			selector = moduleWidgetSelector.select(self.bone.destModule, self.bone.destInfo)
			assert selector, "No selector can be found for %r" % self.destModule

			selector = selector(
				self.bone.destModule,
				**self.bone.destInfo
			)

			conf["selectors"][self.bone.destModule] = selector

		# todo: set context

		# Start widget with selector callback
		selector.setSelector(
			self._addEntriesFromSelection,
			multi=self.bone.multiple,
			allow=self.bone.selectorAllow
		)

	def _addEntriesFromSelection(self, selector, selection):
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

	selectorAllow = (TreeNodeWidget, TreeLeafWidget)

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.formatString = self.boneStructure["format"]
		self.destModule = self.boneStructure["module"]
		self.destInfo = conf["modules"].get(self.destModule)
		self.destStructure = self.boneStructure["relskel"]
		self.dataStructure = self.boneStructure["using"]

		print(self.destModule, self.destInfo)

	@staticmethod
	def checkFor(moduleName, boneName, skelStructure):
		return skelStructure[boneName]["type"] == "relational" or skelStructure[boneName]["type"].startswith("relational.")


boneSelector.insert(1, RelationalBone.checkFor, RelationalBone)

# --- hierarchyBone ---

class HierarchyBone(RelationalBone):  # fixme: this bone is obsolete! It behaves exactly as relational.

	@staticmethod
	def checkFor(moduleName, boneName, skelStructure):
		return skelStructure[boneName]["type"] == "hierarchy" or skelStructure[boneName]["type"].startswith("hierarchy.")

boneSelector.insert(1, HierarchyBone.checkFor, HierarchyBone)

# --- treeItemBone ---

class TreeItemBone(RelationalBone):
	selectorAllow = TreeLeafWidget

	@staticmethod
	def checkFor(moduleName, boneName, skelStructure):
		# fixme: this is rather "relational.tree.leaf" than a "treeitem"...
		return skelStructure[boneName]["type"] == "relational.treeitem" or skelStructure[boneName]["type"].startswith("relational.treeitem.")

boneSelector.insert(2, TreeItemBone.checkFor, TreeItemBone)

# --- treeDirBone ---

class TreeDirBone(RelationalBone):
	selectorAllow = TreeNodeWidget

	@staticmethod
	def checkFor(moduleName, boneName, skelStructure):
		# fixme: this is rather "relational.tree.node" than a "treedir"...
		return skelStructure[boneName]["type"] == "relational.treedir" or skelStructure[boneName]["type"].startswith("relational.treedir.")

boneSelector.insert(2, TreeDirBone.checkFor, TreeDirBone)

# --- fileBone ---

class FileEditWidget(RelationalEditWidget):
	style = ["vi-bone", "vi-bone--file"]

	def _createWidget(self):
		self.previewImg = FilePreviewImage()
		self.appendChild(self.previewImg)

		super()._createWidget()

	def unserialize(self, value=None):
		super().unserialize(value)

		if self.value:
			self.previewImg.setFile(self.value["dest"])


class FileViewWidget(RelationalViewWidget):

	def unserialize(self, value=None):
		self.appendChild(FilePreviewImage(value["dest"] if value else None), replace=True)


class FileBone(TreeItemBone):
	editWidgetFactory = FileEditWidget
	viewWidgetFactory = FileViewWidget

	@staticmethod
	def checkFor(moduleName, boneName, skelStructure):
		#print(moduleName, boneName, skelStructure[boneName]["type"], skelStructure[boneName]["type"] == "relational.file" or skelStructure[boneName]["type"].startswith("relational.file."))
		return skelStructure[boneName]["type"] == "treeitem.file" or skelStructure[boneName]["type"].startswith("treeitem.file.")
		#fixme: This type should be relational.treeitem.file and NOT relational.file.... WTF
		#return skelStructure[boneName]["type"] == "relational.treeitem.file" or skelStructure[boneName]["type"].startswith("relational.treeitem.file.")


boneSelector.insert(3, FileBone.checkFor, FileBone)
