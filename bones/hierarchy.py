# -*- coding: utf-8 -*-
from bones.relational import \
	RelationalMultiSelectionBone, \
	RelationalSingleSelectionBone, \
	RelationalViewBoneDelegate, \
	RelationalBoneExtractor
from config import conf
from priorityqueue import editBoneSelector, viewDelegateSelector, extractorDelegateSelector
from widgets.hierarchy import HierarchyWidget


class HierarchyMultiSelectionBone(RelationalMultiSelectionBone):
	def onShowSelector(self, *args, **kwargs):
		"""
			Opens a TreeWidget sothat the user can select new values
		"""
		currentSelector = HierarchyWidget(self.destModule, selectMode="multi")
		currentSelector.selectionActivatedEvent.register(self)
		conf["mainWindow"].stackWidget(currentSelector)

	def onSelectionActivated(self, table, selection ):
		"""
			Merges the selection made in the TreeWidget into our value(s)
		"""
		self.setSelection([{"dest": x.data, "rel": {}} for x in selection])

class HierarchySingleSelectionBone( RelationalSingleSelectionBone ):
	def onShowSelector(self, *args, **kwargs):
		"""
			Opens a TreeWidget sothat the user can select new values
		"""
		currentSelector = HierarchyWidget(self.destModule, selectMode="single")
		currentSelector.selectionActivatedEvent.register(self)
		conf["mainWindow"].stackWidget(currentSelector)

	def onSelectionActivated(self, table, selection ):
		"""
			Merges the selection made in the TreeWidget into our value(s)
		"""
		self.setSelection([{"dest": x.data, "rel": {}} for x in selection][0])

def CheckForHierarchyBoneSingleSelection(moduleName, boneName, skelStructure, *args, **kwargs):
	isMultiple = "multiple" in skelStructure[boneName].keys() and skelStructure[boneName]["multiple"]
	return CheckForHierarchyBone(moduleName, boneName, skelStructure) and not isMultiple

def CheckForHierarchyBoneMultiSelection(moduleName, boneName, skelStructure, *args, **kwargs):
	isMultiple = "multiple" in skelStructure[boneName].keys() and skelStructure[boneName]["multiple"]
	return CheckForHierarchyBone(moduleName, boneName, skelStructure) and isMultiple

def CheckForHierarchyBone(moduleName, boneName, skelStucture, *args, **kwargs):
	return skelStucture[boneName]["type"].startswith("hierarchy.")

#Register this Bone in the global queue
editBoneSelector.insert(5, CheckForHierarchyBoneSingleSelection, HierarchySingleSelectionBone)
editBoneSelector.insert(5, CheckForHierarchyBoneMultiSelection, HierarchyMultiSelectionBone)
viewDelegateSelector.insert(3, CheckForHierarchyBone, RelationalViewBoneDelegate)
extractorDelegateSelector.insert(3, CheckForHierarchyBone, RelationalBoneExtractor)
