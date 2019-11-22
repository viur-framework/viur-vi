# -*- coding: utf-8 -*-
import html5
from priorityqueue import editBoneSelector, viewDelegateSelector
import bones.string as strBone
# from widgets.edit import InvalidBoneValueException
import re
# import string as py_string

class EmailViewBoneDelegate( strBone.StringViewBoneDelegate ):
	def __init__(self, moduleName, boneName, skelStructure, *args, **kwargs ):
		super( EmailViewBoneDelegate, self ).__init__( moduleName, boneName, skelStructure, *args, **kwargs)

	def getViewElement(self,labelstr,datafield):

		# check if rendering of EmailBones is wanted as String
		if ("params" in self.skelStructure[self.boneName].keys()
			and isinstance(self.skelStructure[self.boneName]["params"], dict)
			and self.skelStructure[self.boneName]["params"].get("renderAsString")):
			return super(EmailViewBoneDelegate, self).getViewElement(labelstr, datafield)

		aa = html5.A()
		aa["href"]="mailto:"+labelstr
		aa["target"]="_Blank"
		aa.appendChild(html5.TextNode(labelstr))
		if not datafield:
			aa["title"]="open mailclient"
		else:
			aa["title"]="open mailclient"+str(datafield)
		return(aa)

class EmailEditBone( strBone.StringEditBone ):
	def __init__(self, moduleName, boneName,readOnly,*args, **kwargs ):
		super( EmailEditBone,  self ).__init__( moduleName, boneName,readOnly, *args, **kwargs )

	@staticmethod
	def isInvalid(value):
		if not value:
			return True
		return not re.match("^[a-zA-Z0-9._%\-+]+@[a-zA-Z0-9._\-]+.[a-zA-Z]{2,6}$", value)

	@staticmethod
	def fromSkelStructure(moduleName, boneName, skelStructure, *args, **kwargs):
		readOnly = "readonly" in skelStructure[ boneName ].keys() and skelStructure[ boneName ]["readonly"]
		if boneName in skelStructure.keys():
			multiple = skelStructure[boneName].get("multiple", False)

		return EmailEditBone(moduleName, boneName, readOnly, multiple=multiple)

	def setSpecialType(self):
		self.input["type"]="email"

	def setExtendedErrorInformation(self, errorInfo ):
		pass


def CheckForEmailBone(  moduleName, boneName, skelStucture, *args, **kwargs ):
	return( skelStucture[boneName]["type"]=="str.email" )

#Register this Bone in the global queue
editBoneSelector.insert( 4, CheckForEmailBone, EmailEditBone)
viewDelegateSelector.insert( 4, CheckForEmailBone, EmailViewBoneDelegate)
