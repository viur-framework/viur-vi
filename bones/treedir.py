#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from event import EventDispatcher

import html5, utils
from priorityqueue import editBoneSelector, viewDelegateSelector, extractorDelegateSelector
from utils import formatString
from widgets.tree import TreeWidget, NodeWidget
from widgets.file import FileWidget, LeafFileWidget
from config import conf
from bones.relational import RelationalMultiSelectionBone, RelationalSingleSelectionBone, RelationalMultiSelectionBoneEntry
from widgets.file import Uploader
from i18n import translate
from network import NetworkService
from widgets.edit import EditWidget
from pane import Pane


class TreeDirMultiSelectionBoneEntry( RelationalMultiSelectionBoneEntry ):
	def __init__(self, *args, **kwargs):
		super( TreeDirMultiSelectionBoneEntry, self ).__init__( *args, **kwargs )
		self["class"].append("fileentry")

		if utils.getImagePreview( self.data ) is not None:
			img = html5.Img()
			img["src"] = utils.getImagePreview( self.data )
			img["class"].append("previewimg")
			self.appendChild(img)
			# Move the img in front of the lbl
			self.element.removeChild( img.element )
			self.element.insertBefore( img.element, self.element.children.item(0) )
		#Remove the editbutton. This wont work on directories; but we maybe need this for other modules?!
		self.removeChild( self.editBtn )
		self.editBtn = None

	def fetchEntry(self, id):
		NetworkService.request(self.modul,"view/node/"+id, successHandler=self.onSelectionDataAviable, cacheable=True)

	def onEdit(self, *args, **kwargs):
		"""
			Edit the image entry.
		"""
		pane = Pane( translate("Edit"), closeable=True, iconClasses=[ "modul_%s" % self.parent.destModul,
		                                                                    "apptype_list", "action_edit" ] )
		conf["mainWindow"].stackPane( pane, focus=True )
		edwg = EditWidget( self.parent.destModul, EditWidget.appTree, key=self.data[ "id" ], skelType="leaf"  )
		pane.addWidget( edwg )

class TreeDirMultiSelectionBone( RelationalMultiSelectionBone ):

	def __init__(self, *args, **kwargs):
		if "destModul" in kwargs:
			kwargs["destModul"] = kwargs["destModul"][ : kwargs["destModul"].find("_") ] # Remove _rootNode
		super(TreeDirMultiSelectionBone, self).__init__( *args, **kwargs )


	def onUploadSuccess(self, uploader, file ):
		self.setSelection( [file] )


	def onShowSelector(self, *args, **kwargs):
		"""
			Opens a TreeWidget sothat the user can select new values
		"""
		currentSelector = FileWidget( self.destModul, isSelector="node" )
		currentSelector.selectionReturnEvent.register( self )
		conf["mainWindow"].stackWidget( currentSelector )
		self.parent()["class"].append("is_active")

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
		self.setSelection( [x.data for x in selection if isinstance(x,NodeWidget)] )

	def setSelection(self, selection):
		"""
			Set our current value to 'selection'
			@param selection: The new entry that this bone should reference
			@type selection: dict
		"""
		if selection is None:
			return
		for data in selection:
			entry = TreeDirMultiSelectionBoneEntry( self, self.destModul, data)
			self.addEntry( entry )

class TreeDirSingleSelectionBone( RelationalSingleSelectionBone ):

	def __init__(self, *args, **kwargs):
		if "destModul" in kwargs:
			kwargs["destModul"] = kwargs["destModul"][ : kwargs["destModul"].find("_") ] # Remove _rootNode
		print( "xx%syy" % kwargs["destModul"])
		super(TreeDirSingleSelectionBone, self).__init__( *args, **kwargs )

		self.previewImg = html5.Img()
		self.previewImg["class"].append("previewimg")
		self.appendChild( self.previewImg )


	def onShowSelector(self, *args, **kwargs):
		"""
			Opens a TreeWidget sothat the user can select new values
		"""
		currentSelector = TreeWidget( self.destModul, isSelector="node" )
		currentSelector.selectionReturnEvent.register( self )
		conf["mainWindow"].stackWidget( currentSelector )
		self.parent()["class"].append("is_active")

	def onSelectionReturn(self, table, selection ):
		"""
			Merges the selection made in the TreeWidget into our value(s)
		"""
		print(" GOT TREEDIR onSelectionReturn CALL")
		hasValidSelection = False
		for s in selection:
			if isinstance( s, NodeWidget ):
				hasValidSelection = True
				break
		if not hasValidSelection: #Its just a folder that's been activated
			return
		self.setSelection( [x.data for x in selection if isinstance(x,NodeWidget)][0] )

	def onEdit(self, *args, **kwargs):
		"""
			Edit the image.
		"""
		if not self.selection:
			return

		pane = Pane( translate("Edit"), closeable=True, iconClasses=[ "modul_%s" % self.destModul,
		                                                                    "apptype_list", "action_edit" ] )
		conf["mainWindow"].stackPane( pane, focus=True )
		edwg = EditWidget( self.destModul, EditWidget.appTree, key=self.selection[ "id" ], skelType="leaf"  )
		pane.addWidget( edwg )

	def setSelection(self, selection):
		"""
			Set our current value to 'selection'
			@param selection: The new entry that this bone should reference
			@type selection: dict
		"""
		self.selection = selection
		if selection:
			NetworkService.request( self.destModul, "view/node/"+selection["id"],
			                                successHandler=self.onSelectionDataAviable, cacheable=True)
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



def CheckForTreeDirBoneSingleSelection( modulName, boneName, skelStructure, *args, **kwargs ):
	isMultiple = "multiple" in skelStructure[boneName].keys() and skelStructure[boneName]["multiple"]
	return CheckForTreeDirBone( modulName, boneName, skelStructure ) and not isMultiple

def CheckForTreeDirBoneMultiSelection( modulName, boneName, skelStructure, *args, **kwargs ):
	isMultiple = "multiple" in skelStructure[boneName].keys() and skelStructure[boneName]["multiple"]
	return CheckForTreeDirBone( modulName, boneName, skelStructure ) and isMultiple

def CheckForTreeDirBone(  modulName, boneName, skelStucture, *args, **kwargs ):
	#print("CHECKING FILE BONE", skelStucture[boneName]["type"])
	print( skelStucture[boneName]["type"] )
	return( skelStucture[boneName]["type"].startswith("relational.treedir.") )

#Register this Bone in the global queue
editBoneSelector.insert( 5, CheckForTreeDirBoneSingleSelection, TreeDirSingleSelectionBone)
editBoneSelector.insert( 5, CheckForTreeDirBoneMultiSelection, TreeDirMultiSelectionBone)
#viewDelegateSelector.insert( 3, CheckForTreeDirBone, FileViewBoneDelegate)
#extractorDelegateSelector.insert(3, CheckForTreeDirBone, FileBoneExtractor)
