# -*- coding: utf-8 -*-
import html5

from priorityqueue import editBoneSelector, viewDelegateSelector, extractorDelegateSelector
from config import conf

class BaseBoneExtractor(object):
	"""
		Base "Catch-All" extractor for everything not handled separately.
	"""
	def __init__(self, moduleName, boneName, skelStructure, *args, **kwargs):
		super(BaseBoneExtractor, self).__init__()
		self.skelStructure = skelStructure
		self.boneName = boneName
		self.moduleName = moduleName

	def render(self, data, field):
		if field in data.keys():
			return str(data[field])

		return conf["empty_value"]

	def raw(self, data, field):
		if field in data.keys():
			if isinstance(data[field], list):
				return [str(x) for x in data[field]]

			return str(data[field])

		return None

class BaseViewBoneDelegate( object ):
	"""
		Base "Catch-All" delegate for everything not handled separately.
	"""
	def __init__(self, moduleName, boneName, skelStructure, *args, **kwargs ):
		super(BaseViewBoneDelegate, self).__init__()
		self.skelStructure = skelStructure
		self.boneName = boneName
		self.moduleName=moduleName

	def render(self, data, field):
		if field in data.keys():
			return html5.Label(str(data[field]))

		return html5.Label(conf[ "empty_value" ])


class BaseEditBone(html5.Input):
	"""
		Base edit widget for everything not handled separately.
	"""
	def __init__(self, moduleName, boneName, readOnly, *args, **kwargs):
		super(BaseEditBone, self).__init__(*args, **kwargs)
		self.boneName = boneName
		self.readOnly = readOnly
		self.setParams()

	@staticmethod
	def fromSkelStructure(moduleName, boneName, skelStructure):
		return BaseEditBone(moduleName, boneName, skelStructure[boneName].get("readonly", False))

	def setParams(self):
		if self.readOnly:
			self["disabled"] = True

	def unserialize(self, data, extendedErrorInformation = None):
		if self.boneName in data.keys():
			self["value"] = data.get(self.boneName, "")

	def serializeForPost(self):
		return {
			self.boneName: self["value"]
		}

	def serializeForDocument(self):
		return self.serializeForPost()

	def setExtendedErrorInformation(self, errorInfo):
		pass

class BaseLabelBone(html5.Label):
	"""
		Show bone as (readonly) label.
	"""
	def __init__(self, moduleName, boneName, *args, **kwargs):
		super(BaseLabelBone, self).__init__(*args, **kwargs)
		self.boneName = boneName
		self.value = None

	@staticmethod
	def fromSkelStructure(moduleName, boneName, skelStructure):
		return BaseLabelBone(moduleName, boneName)

	@staticmethod
	def checkForLabelStyle(moduleName, boneName, skelStructure):
		if boneName in skelStructure.keys():
			if "params" in skelStructure[boneName] and skelStructure[boneName]["params"]:
				return skelStructure[boneName]["params"].get("style") == "label"

		return False

	def unserialize(self, data, extendedErrorInformation = None):
		if self.boneName in data.keys():
			self.value = data.get(self.boneName, "")

			self.removeAllChildren()
			self.appendChild(self.value)

	def serializeForPost(self):
		return {
			self.boneName: self.value
		}

	def serializeForDocument(self):
		return self.serializeForPost()

	def setExtendedErrorInformation(self, errorInfo):
		pass

# Register this Bone in the global queue as generic fallback.

editBoneSelector.insert(10, BaseLabelBone.checkForLabelStyle, BaseLabelBone)
editBoneSelector.insert(0, lambda *args, **kwargs: True, BaseEditBone)
viewDelegateSelector.insert(0, lambda *args, **kwargs: True, BaseViewBoneDelegate)
extractorDelegateSelector.insert(0, lambda *args, **kwargs: True, BaseBoneExtractor)
