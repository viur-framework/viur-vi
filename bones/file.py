# -*- coding: utf-8 -*-
from vi import html5

from vi.priorityqueue import boneSelector
from vi.config import conf
from vi.bones.relational import RelationalBone, RelationalEditWidget, RelationalMultiEditWidget, RelationalViewWidget, _getDefaultValues

from vi.widgets.file import FileWidget, LeafFileWidget, Uploader, FilePreviewImage


class FileEditWidget(RelationalEditWidget):
	style = ["vi-bone", "vi-bone--file"]

	def _createWidget(self):
		self.previewImg = FilePreviewImage()
		self.appendChild(self.previewImg)

		self.fromHTML(
			"""
				<ignite-input [name]="destWidget" readonly>
				<button [name]="selectBtn" class="btn--select" text="Select" icon="icons-select"></button>
			"""
		)

	def unserialize(self, value=None):
		super().unserialize(value)

		if self.value:
			self.previewImg.setFile(self.value["dest"])

	def onSelectBtnClick(self):
		# Configure file selector
		fileSelector = conf.get("fileSelector")

		if not fileSelector or conf["mainWindow"].containsWidget(fileSelector):
			fileSelector = FileWidget(self.bone.boneStructure["module"], selectMode="single.leaf")
		else:
			fileSelector.selectMode = "single.leaf"

		if not conf.get("fileSelector"):
			conf["fileSelector"] = fileSelector

		fileSelector.selectionReturnEvent.register(self, reset=True)

		conf["mainWindow"].stackWidget(fileSelector)
		self.parent().addClass("is-active")

	def onSelectionReturn(self, table, selection):
		self.unserialize({"dest": selection[0].data, "rel": None})
		#self.changeEvent.fire(self)  #fixme ...


class FileViewWidget(RelationalViewWidget):

	def unserialize(self, value=None):
		self.appendChild(FilePreviewImage(value["dest"] if value else None), replace=True)


class FileMultiEditWidget(RelationalMultiEditWidget):

	def onAddBtnClick(self):
		# Configure file selector
		fileSelector = conf.get("fileSelector")

		if not fileSelector or conf["mainWindow"].containsWidget(fileSelector):
			fileSelector = FileWidget(self.bone.boneStructure["module"], selectMode="multi.leaf")
		else:
			fileSelector.selectMode = "multi.leaf"

		if not conf.get("fileSelector"):
			conf["fileSelector"] = fileSelector

		fileSelector.selectionReturnEvent.register(self, reset=True)

		conf["mainWindow"].stackWidget(fileSelector)
		self.parent().addClass("is-active")

	def onSelectionReturn(self, table, selection):
		for entry in selection:
			self.addEntry({
				"dest": entry.data,
				"rel": _getDefaultValues(self.bone.boneStructure["using"])
							if self.bone.boneStructure["using"] else None
			})


class FileBone(RelationalBone):
	editWidgetFactory = FileEditWidget
	viewWidgetFactory = FileViewWidget
	multiEditWidgetFactory = FileMultiEditWidget

	@staticmethod
	def checkFor(moduleName, boneName, skelStructure):
		return skelStructure[boneName]["type"] == "treeitem.file" or skelStructure[boneName]["type"].startswith("treeitem.file.")


boneSelector.insert(1, FileBone.checkFor, FileBone)
