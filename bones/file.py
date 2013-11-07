#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import html5
from priorityqueue import editBoneSelector, viewDelegateSelector
from utils import formatString
from widgets.tree import TreeWidget
from config import conf
from bones.relational import RelationalMultiSelectionBone, RelationalSingleSelectionBone




class FileMultiSelectionBone( RelationalMultiSelectionBone ):
	def onShowSelector(self, *args, **kwargs):
		"""
			Opens a TreeWidget sothat the user can select new values
		"""
		assert self.currentSelector is None, "Whoops... Attempt to open a second selector for this bone!"
		self.currentSelector = TreeWidget( self.destModul )
		self.currentSelector.selectionActivatedEvent.register( self )
		conf["mainWindow"].stackWidget( self.currentSelector )

	def onSelectionActivated(self, table, selection ):
		"""
			Merges the selection made in the TreeWidget into our value(s)
		"""
		assert self.currentSelector is not None, "Whoops... Got a new selection while not having an open selector!"
		hasValidSelection = False
		for s in selection:
			if isinstance( s, self.currentSelector.leafWidget ):
				hasValidSelection = True
				break
		if not hasValidSelection: #Its just a folder that's been activated
			return
		conf["mainWindow"].removeWidget( self.currentSelector )
		self.setSelection( [x.data for x in selection if isinstance(x,self.currentSelector.leafWidget)] )
		self.currentSelector = None

class FileSingleSelectionBone( RelationalSingleSelectionBone ):
	def onShowSelector(self, *args, **kwargs):
		"""
			Opens a TreeWidget sothat the user can select new values
		"""
		assert self.currentSelector is None, "Whoops... Attempt to open a second selector for this bone!"
		self.currentSelector = TreeWidget( self.destModul )
		self.currentSelector.selectionActivatedEvent.register( self )
		conf["mainWindow"].stackWidget( self.currentSelector )

	def onSelectionActivated(self, table, selection ):
		"""
			Merges the selection made in the TreeWidget into our value(s)
		"""
		assert self.currentSelector is not None, "Whoops... Got a new selection while not having an open selector!"
		hasValidSelection = False
		for s in selection:
			if isinstance( s, self.currentSelector.leafWidget ):
				hasValidSelection = True
				break
		if not hasValidSelection: #Its just a folder that's been activated
			return
		conf["mainWindow"].removeWidget( self.currentSelector )
		self.setSelection( [x.data for x in selection if isinstance(x,self.currentSelector.leafWidget)][0] )
		self.currentSelector = None





def CheckForFileBoneSingleSelection( modulName, boneName, skelStructure ):
	isMultiple = "multiple" in skelStructure[boneName].keys() and skelStructure[boneName]["multiple"]
	return CheckForFileBone( modulName, boneName, skelStructure ) and not isMultiple

def CheckForFileBoneMultiSelection( modulName, boneName, skelStructure ):
	isMultiple = "multiple" in skelStructure[boneName].keys() and skelStructure[boneName]["multiple"]
	return CheckForFileBone( modulName, boneName, skelStructure ) and isMultiple

def CheckForFileBone(  modulName, boneName, skelStucture ):
	print("CHECKING FILE BONE", skelStucture[boneName]["type"])
	return( skelStucture[boneName]["type"].startswith("treeitem.file") )

#Register this Bone in the global queue
editBoneSelector.insert( 5, CheckForFileBoneSingleSelection, FileSingleSelectionBone)
editBoneSelector.insert( 5, CheckForFileBoneMultiSelection, FileMultiSelectionBone)