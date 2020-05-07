# -*- coding: utf-8 -*-
import re

from vi import html5

from vi.priorityqueue import editBoneSelector, viewDelegateSelector
from vi.exception import InvalidBoneValueException

from vi.bones.string import StringViewBoneDelegate, StringEditBone


class EmailViewBoneDelegate(StringViewBoneDelegate):

	def getViewElement(self, labelstr, datafield):
		# check if rendering of EmailBones is wanted as String
		if ("params" in self.skelStructure[self.boneName].keys()
				and isinstance(self.skelStructure[self.boneName]["params"], dict)
				and self.skelStructure[self.boneName]["params"].get("renderAsString")):
			return super(EmailViewBoneDelegate, self).getViewElement(labelstr, datafield)

		delegato = html5.Div(labelstr)
		delegato.addClass("vi-delegato", "vi-delegato--mail")

		return delegato


class EmailEditBone(StringEditBone):

	@staticmethod
	def fromSkelStructure(moduleName, boneName, skelStructure, *args, **kwargs):
		readOnly = "readonly" in skelStructure[boneName].keys() and skelStructure[boneName]["readonly"]
		return EmailEditBone(moduleName, boneName, readOnly)

	def unserialize(self, data):
		if self.boneName in data.keys():
			self.input["value"] = data[self.boneName] if data[self.boneName] else ""

	def serializeForPost(self):
		if not self["value"] or re.match("^[a-zA-Z0-9._%-+]+@[a-zA-Z0-9._-]+.[a-zA-Z]{2,6}$", self.input["value"]):
			return {self.boneName: self.input["value"]}
		raise InvalidBoneValueException()

	def setSpecialType(self):
		self.input["type"] = "email"

	def setExtendedErrorInformation(self, errorInfo):
		pass


def CheckForEmailBone(moduleName, boneName, skelStucture, *args, **kwargs):
	return skelStucture[boneName]["type"] == "str.email"


# Register this Bone in the global queue
editBoneSelector.insert(4, CheckForEmailBone, EmailEditBone)
viewDelegateSelector.insert(4, CheckForEmailBone, EmailViewBoneDelegate)
