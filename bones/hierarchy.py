# -*- coding: utf-8 -*-
from vi.bones.relational import \
	RelationalBone,\
	RelationalViewBoneDelegate, \
	RelationalBoneExtractor
from vi.config import conf
from vi.priorityqueue import editBoneSelector, viewDelegateSelector, extractorDelegateSelector
from vi.widgets.hierarchy import HierarchyWidget


class HierarchyBone(RelationalBone):

	def __init__(self, srcModule, boneName, readOnly, destModule,
	                format="$(dest.name)", using=None, usingDescr=None,
	                relskel=None, context = None, multiple=False,params=None, *args, **kwargs):
		if params and "vi.style" in params and params["vi.style"] =="quickselect":
			params["vi.style"] = None

		super().__init__(srcModule, boneName, readOnly, destModule,
	                format, using, usingDescr,
	                relskel, context, multiple, params, *args, **kwargs)

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
		self.changeEvent.fire( self )

def CheckForHierarchyBoneSingleSelection(moduleName, boneName, skelStructure, *args, **kwargs):
	isMultiple = "multiple" in skelStructure[boneName].keys() and skelStructure[boneName]["multiple"]
	return CheckForHierarchyBone(moduleName, boneName, skelStructure) and not isMultiple

def CheckForHierarchyBoneMultiSelection(moduleName, boneName, skelStructure, *args, **kwargs):
	isMultiple = "multiple" in skelStructure[boneName].keys() and skelStructure[boneName]["multiple"]
	return CheckForHierarchyBone(moduleName, boneName, skelStructure) and isMultiple

def CheckForHierarchyBone(moduleName, boneName, skelStucture, *args, **kwargs):
	return skelStucture[boneName]["type"].startswith("hierarchy.")

#Register this Bone in the global queue
editBoneSelector.insert(5, CheckForHierarchyBoneSingleSelection, HierarchyBone)
editBoneSelector.insert(5, CheckForHierarchyBoneMultiSelection, HierarchyBone)
viewDelegateSelector.insert(3, CheckForHierarchyBone, RelationalViewBoneDelegate)
extractorDelegateSelector.insert(3, CheckForHierarchyBone, RelationalBoneExtractor)
