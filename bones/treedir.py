# -*- coding: utf-8 -*-
import html5
import utils
from bones.relational import RelationalMultiSelectionBone, RelationalSingleSelectionBone, \
	RelationalMultiSelectionBoneEntry
from config import conf
from i18n import translate
from network import NetworkService
from pane import Pane
from priorityqueue import editBoneSelector
from widgets.edit import EditWidget
from widgets.file import FileWidget
from widgets.tree import TreeWidget, NodeWidget


class TreeDirMultiSelectionBoneEntry(RelationalMultiSelectionBoneEntry):
	def __init__(self, *args, **kwargs):
		super(TreeDirMultiSelectionBoneEntry, self).__init__(*args, **kwargs)
		self.addClass("fileentry")

		src = utils.getImagePreview(self.data)

		if src is not None:
			img = html5.Img()
			img["src"] = src
			img.addClass("vi-tree-filepreview")
			self.appendChild(img)

			# Move the img in front of the lbl
			self.element.removeChild(img.element)
			self.element.insertBefore(img.element, self.element.children.item(0))

		#Remove the editbutton. This won't work on directories; but we maybe need this for other modules?!
		self.removeChild(self.editBtn)
		self.editBtn = None

	def fetchEntry(self, key):
		NetworkService.request(self.module, "view/node/%s" % key,
		                        successHandler=self.onSelectionDataAviable,
		                        cacheable=True)

	def onEdit(self, *args, **kwargs):
		"""
			Edit the image entry.
		"""
		pane = Pane( translate("Edit"), closeable=True, iconURL="icons-edit", iconClasses=[ "modul_%s" % self.parent.destModule,
		                                                                    "apptype_list", "action_edit" ] )
		conf["mainWindow"].stackPane( pane, focus=True )
		edwg = EditWidget( self.parent.destModule, EditWidget.appTree, key=self.data[ "key" ], skelType="leaf"  )
		pane.addWidget( edwg )

class TreeDirMultiSelectionBone( RelationalMultiSelectionBone ):

	def __init__(self, *args, **kwargs):
		if "destModule" in kwargs:
			kwargs["destModule"] = kwargs["destModule"][ : kwargs["destModule"].find("_") ] # Remove _rootNode
		super(TreeDirMultiSelectionBone, self).__init__( *args, **kwargs )

	def onUploadSuccess(self, uploader, file ):
		self.setSelection( [file] )

	def onShowSelector(self, *args, **kwargs):
		"""
			Opens a TreeWidget sothat the user can select new values
		"""
		currentSelector = FileWidget(self.destModule, selectMode="single.node")
		currentSelector.selectionReturnEvent.register( self )
		conf["mainWindow"].stackWidget( currentSelector )
		self.parent().addClass("is-active")

	def onSelectionReturn(self, table, selection ):
		"""
			Merges the selection made in the TreeWidget into our value(s)
		"""
		hasValidSelection = False
		for s in selection:
			if isinstance( s, NodeWidget ):
				hasValidSelection = True
				break
		if not hasValidSelection: #Its just a folder that's been activated
			return

		self.setSelection([{"dest": x.data, "rel": {}} for x in selection if isinstance(x,NodeWidget)])

	def setSelection(self, selection):
		"""
			Set our current value to 'selection'

			@param selection: The new entry that this bone should reference
			@type selection: dict | list
		"""
		if selection is None:
			return

		for data in selection:
			entry = TreeDirMultiSelectionBoneEntry( self, self.destModule, data)
			self.addEntry( entry )

class TreeDirSingleSelectionBone( RelationalSingleSelectionBone ):

	def __init__(self, *args, **kwargs):
		print("kwargs", kwargs)
		if "destModule" in kwargs:
			kwargs["destModule"] = kwargs["destModule"][ : kwargs["destModule"].find("_") ] # Remove _rootNode
		# print( "xx%syy" % kwargs["destModul"])
		super(TreeDirSingleSelectionBone, self).__init__( *args, **kwargs )

		self.previewImg = html5.Img()
		self.previewImg.addClass("vi-tree-filepreview")
		self.appendChild( self.previewImg )


	def onShowSelector(self, *args, **kwargs):
		"""
			Opens a TreeWidget sothat the user can select new values
		"""
		currentSelector = TreeWidget(self.destModule, selectMode="single.node")
		currentSelector.selectionReturnEvent.register( self )
		conf["mainWindow"].stackWidget( currentSelector )
		self.parent().addClass("is-active")

	def onSelectionReturn(self, table, selection ):
		"""
			Merges the selection made in the TreeWidget into our value(s)
		"""
		hasValidSelection = False
		for s in selection:
			if isinstance( s, NodeWidget ):
				hasValidSelection = True
				break
		if not hasValidSelection: #Its just a folder that's been activated
			return
		self.setSelection([{"dest": x.data, "rel": {}} for x in selection if isinstance(x, NodeWidget)][0])

	def onEdit(self, *args, **kwargs):
		"""
			Edit the image.
		"""
		if not self.selection:
			return

		pane = Pane( translate("Edit"), closeable=True, iconURL="icons-edit", iconClasses=[ "modul_%s" % self.destModule,
		                                                                    "apptype_list", "action_edit" ] )
		conf["mainWindow"].stackPane( pane, focus=True )
		edwg = EditWidget( self.destModule, EditWidget.appTree, key=self.selection[ "key" ], skelType="leaf"  )
		pane.addWidget( edwg )

	def setSelection(self, selection):
		"""
			Set our current value to 'selection'
			@param selection: The new entry that this bone should reference
			@type selection: dict
		"""
		self.selection = selection
		if selection:
			NetworkService.request( self.destModule, "view/node/"+selection["dest"]["key"],
			                                successHandler=self.onSelectionDataAvailable, cacheable=True)
			self.selectionTxt["value"] = translate("Loading...")

			if utils.getImagePreview( self.selection ) is not None:
				self.previewImg["src"] = utils.getImagePreview( self.selection )
				self.previewImg["style"]["display"] = ""
			else:
				self.previewImg["style"]["display"] = "none"
		else:
			self.selectionTxt["value"] = ""
			self.previewImg["style"]["display"] = "none"

		self.updateButtons()



def CheckForTreeDirBoneSingleSelection(moduleName, boneName, skelStructure, *args, **kwargs):
	isMultiple = "multiple" in skelStructure[boneName].keys() and skelStructure[boneName]["multiple"]
	return CheckForTreeDirBone(moduleName, boneName, skelStructure) and not isMultiple

def CheckForTreeDirBoneMultiSelection(moduleName, boneName, skelStructure, *args, **kwargs):
	isMultiple = "multiple" in skelStructure[boneName].keys() and skelStructure[boneName]["multiple"]
	return CheckForTreeDirBone(moduleName, boneName, skelStructure) and isMultiple

def CheckForTreeDirBone(moduleName, boneName, skelStucture, *args, **kwargs):
	return skelStucture[boneName]["type"].startswith("treedir.")

#Register this Bone in the global queue
editBoneSelector.insert( 5, CheckForTreeDirBoneSingleSelection, TreeDirSingleSelectionBone)
editBoneSelector.insert( 5, CheckForTreeDirBoneMultiSelection, TreeDirMultiSelectionBone)
