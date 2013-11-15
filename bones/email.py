#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import html5
from priorityqueue import editBoneSelector, viewDelegateSelector
from config import conf
import bones.string as strBone

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
	def __init__(self, modulName, boneName,readOnly,skelStructure=False,*args, **kwargs ):
		super( EmailEditBone,  self ).__init__( modulName, boneName,readOnly,skelStructure, *args, **kwargs )

	def setSpecialType(self):
		self.input["type"]="email"

def CheckForEmailBone(  modulName, boneName, skelStucture ):
	return( skelStucture[boneName]["type"]=="str.email" )

#Register this Bone in the global queue
editBoneSelector.insert( 4, CheckForEmailBone, EmailEditBone)
viewDelegateSelector.insert( 4, CheckForEmailBone, EmailViewBoneDelegate)
