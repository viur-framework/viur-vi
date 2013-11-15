#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import html5
from priorityqueue import editBoneSelector, viewDelegateSelector
from utils import formatString
from widgets.hierarchy import HierarchyWidget
from config import conf
from bones.relational import RelationalMultiSelectionBone, RelationalSingleSelectionBone




class HierarchyMultiSelectionBone( RelationalMultiSelectionBone ):
	def onShowSelector(self, *args, **kwargs):
		"""
			Opens a TreeWidget sothat the user can select new values
		"""
		assert self.currentSelector is None, "Whoops... Attempt to open a second selector for this bone!"
		self.currentSelector = HierarchyWidget( self.destModul )
		self.currentSelector.selectionActivatedEvent.register( self )
		conf["mainWindow"].stackWidget( self.currentSelector )

	def onSelectionActivated(self, table, selection ):
		"""
			Merges the selection made in the TreeWidget into our value(s)
		"""
		assert self.currentSelector is not None, "Whoops... Got a new selection while not having an open selector!"
		conf["mainWindow"].removeWidget( self.currentSelector )
		self.setSelection( [x.data for x in selection] )
		self.currentSelector = None

class HierarchySingleSelectionBone( RelationalSingleSelectionBone ):
	def onShowSelector(self, *args, **kwargs):
		"""
			Opens a TreeWidget sothat the user can select new values
		"""
		assert self.currentSelector is None, "Whoops... Attempt to open a second selector for this bone!"
		self.currentSelector = HierarchyWidget( self.destModul )
		self.currentSelector.selectionActivatedEvent.register( self )
		conf["mainWindow"].stackWidget( self.currentSelector )

	def onSelectionActivated(self, table, selection ):
		"""
			Merges the selection made in the TreeWidget into our value(s)
		"""
		assert self.currentSelector is not None, "Whoops... Got a new selection while not having an open selector!"
		conf["mainWindow"].removeWidget( self.currentSelector )
		self.setSelection( [x.data for x in selection][0] )
		self.currentSelector = None





def CheckForHierarchyBoneSingleSelection( modulName, boneName, skelStructure ):
	isMultiple = "multiple" in skelStructure[boneName].keys() and skelStructure[boneName]["multiple"]
	return CheckForHierarchyBone( modulName, boneName, skelStructure ) and not isMultiple

def CheckForHierarchyBoneMultiSelection( modulName, boneName, skelStructure ):
	isMultiple = "multiple" in skelStructure[boneName].keys() and skelStructure[boneName]["multiple"]
	return CheckForHierarchyBone( modulName, boneName, skelStructure ) and isMultiple

def CheckForHierarchyBone(  modulName, boneName, skelStucture ):
	return( skelStucture[boneName]["type"].startswith("hierarchy.") )

#Register this Bone in the global queue
editBoneSelector.insert( 5, CheckForHierarchyBoneSingleSelection, HierarchySingleSelectionBone)
editBoneSelector.insert( 5, CheckForHierarchyBoneMultiSelection, HierarchyMultiSelectionBone)