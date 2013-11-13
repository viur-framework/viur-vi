#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import html5
from priorityqueue import editBoneSelector, viewDelegateSelector

class TextViewBoneDelegate( object ):
	def __init__(self, modulName, boneName, skelStructure, *args, **kwargs ):
		super( TextViewBoneDelegate, self ).__init__()
		self.skelStructure = skelStructure
		self.boneName = boneName
		self.modulName=modulName

	def render( self, data, field ):
		if field in data.keys():
			return( html5.Label(str( data[field])))
		return( html5.Label("..") )

class TextEditBone( html5.Textarea ):

	def __init__(self, modulName, boneName,readOnly, *args, **kwargs ):
		super( TextEditBone,  self ).__init__( *args, **kwargs )
		self.boneName = boneName
		self.readOnly = readOnly

	@staticmethod
	def fromSkelStructure( modulName, boneName, skelStructure ):
		readOnly = "readonly" in skelStructure[ boneName ].keys() and skelStructure[ boneName ]["readonly"]
		return( TextEditBone( modulName, boneName, readOnly ) )

	def unserialize(self, data):
		if self.boneName in data.keys():
			self["value"] = data[ self.boneName ] if data[ self.boneName ] else ""

	def serializeForPost(self):
			return( { self.boneName: self["value"] } )

	def serializeForDocument(self):
		return( self.serialize( ) )

def CheckForTextBone(  modulName, boneName, skelStucture ):
	return( skelStucture[boneName]["type"]=="text" )

#Register this Bone in the global queue
editBoneSelector.insert( 3, CheckForTextBone, TextEditBone)
viewDelegateSelector.insert( 3, CheckForTextBone, TextViewBoneDelegate)
