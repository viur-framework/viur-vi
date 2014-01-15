#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import html5
from priorityqueue import editBoneSelector, viewDelegateSelector
from config import conf
import bones.string as strBone
from widgets.edit import InvalidBoneValueException
import re

class EmailViewBoneDelegate( strBone.StringViewBoneDelegate ):
	def __init__(self, modulName, boneName, skelStructure, *args, **kwargs ):
		super( EmailViewBoneDelegate, self ).__init__( modulName, boneName, skelStructure, *args, **kwargs)


	def getViewElement(self,labelstr,datafield):
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
	def __init__(self, modulName, boneName,readOnly,*args, **kwargs ):
		super( EmailEditBone,  self ).__init__( modulName, boneName,readOnly, *args, **kwargs )

	@staticmethod
	def fromSkelStructure( modulName, boneName, skelStructure ):
		readOnly = "readonly" in skelStructure[ boneName ].keys() and skelStructure[ boneName ]["readonly"]
		return( EmailEditBone( modulName, boneName, readOnly ) )

	def unserialize(self, data):
		if self.boneName in data.keys():
			self.input["value"] = data[ self.boneName ] if data[ self.boneName ] else ""

	def serializeForPost(self):
		if not self["value"] or re.match("^[a-zA-Z0-9._%-+]+@[a-zA-Z0-9._-]+.[a-zA-Z]{2,6}$",self.input["value"]):
			return( { self.boneName: self.input["value"] } )
		raise InvalidBoneValueException()


	def setSpecialType(self):
		self.input["type"]="email"

def CheckForEmailBone(  modulName, boneName, skelStucture ):
	return( skelStucture[boneName]["type"]=="str.email" )

#Register this Bone in the global queue
editBoneSelector.insert( 4, CheckForEmailBone, EmailEditBone)
viewDelegateSelector.insert( 4, CheckForEmailBone, EmailViewBoneDelegate)
