#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import html5
from priorityqueue import editBoneSelector, viewDelegateSelector
from config import conf
import bones.string as strBone

class EmailViewBoneDelegate( strBone.StringViewBoneDelegate ):
	def __init__(self, modulName, boneName, skelStructure, *args, **kwargs ):
		super( EmailViewBoneDelegate, self ).__init__( modulName, boneName, skelStructure, *args, **kwargs)
		print("Boom Boom Boom Boom")


class EmailEditBone( strBone.StringEditBone ):
	def __init__(self, modulName, boneName,readOnly,skelStructure=False,*args, **kwargs ):
		super( EmailEditBone,  self ).__init__( modulName, boneName,readOnly,skelStructure, *args, **kwargs )
		print("Boom Boom Boom Boom")

	def setSpecialType(self):
		self.input["type"]="email"

def CheckForEmailBone(  modulName, boneName, skelStucture ):
	print("Boom Boom Boom Boom Type:"+skelStucture[boneName]["type"])
	return( skelStucture[boneName]["type"]=="str.email" )

#Register this Bone in the global queue
editBoneSelector.insert( 4, CheckForEmailBone, EmailEditBone)
viewDelegateSelector.insert( 4, CheckForEmailBone, EmailViewBoneDelegate)
