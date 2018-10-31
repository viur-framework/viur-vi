# -*- coding: utf-8 -*-
import html5, re
from priorityqueue import editBoneSelector, viewDelegateSelector
from exception import InvalidBoneValueException
from i18n import translate

class PasswordEditBone( html5.Div ):
	def __init__(self, moduleName, boneName, readOnly, verify = True, *args, **kwargs ):
		super( PasswordEditBone,  self ).__init__( *args, **kwargs )
		self.boneName = boneName
		self.readOnly = readOnly

		self.primeinput = html5.Input()
		self.primeinput["type"] = "password"
		self.appendChild(self.primeinput)

		if verify and not readOnly:

			lbl = html5.Label(translate("reenter password"))
			lbl["for"] = (moduleName or "") + "_" + boneName + "_reenterpwd"
			self.appendChild(lbl)

			self.secondinput = html5.Input()
			self.secondinput["type"] = "password"
			self.secondinput["name"] = lbl["for"]
			self.appendChild(self.secondinput)
		else:
			self.secondinput = None

		if self.readOnly:
			self["disabled"] = True

	@staticmethod
	def fromSkelStructure(moduleName, boneName, skelStructure, *args, **kwargs):
		verify = True
		if ("params" in skelStructure[boneName]
		    and skelStructure[boneName]["params"]):
			verify = skelStructure[boneName]["params"].get("verify", True)

		readOnly = skelStructure[boneName].get("readonly", False)

		return PasswordEditBone(moduleName, boneName, readOnly, verify)

	def unserialize(self, data):
		pass

	def serializeForPost(self):
		if not self.secondinput or self.primeinput["value"] == self.secondinput["value"]:
			return {self.boneName: self.primeinput["value"]}

		raise InvalidBoneValueException()

	def serializeForDocument(self):
		return {self.boneName: self.primeinput["value"]}

	def setExtendedErrorInformation(self, errorInfo ):
		pass


def CheckForPasswordBone(  moduleName, boneName, skelStucture, *args, **kwargs ):
	return str(skelStucture[boneName]["type"]).startswith("password")

#Register this Bone in the global queue
editBoneSelector.insert( 5, CheckForPasswordBone, PasswordEditBone)


