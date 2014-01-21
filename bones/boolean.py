#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import html5
from priorityqueue import editBoneSelector, viewDelegateSelector
from config import conf

class BooleanViewBoneDelegate( object ):
	def __init__(self, modulName, boneName, skelStructure, *args, **kwargs ):
		super( BooleanViewBoneDelegate, self ).__init__()
		self.skelStructure = skelStructure
		self.boneName = boneName
		self.modulName = modulName

	def render( self, data, field ):
		if field in data.keys():
			return( html5.Label(str( data[field])))
		return( html5.Label("..") )

class BooleanEditBone( html5.Input ):

	def __init__(self, modulName, boneName,readOnly, *args, **kwargs ):
		super( BooleanEditBone,  self ).__init__( *args, **kwargs )
		self.boneName = boneName
		self.readOnly = readOnly
		self["type"]="checkbox"
		if readOnly:
			self["disabled"]=True


	@staticmethod
	def fromSkelStructure( modulName, boneName, skelStructure ):
		readOnly = "readonly" in skelStructure[ boneName ].keys() and skelStructure[ boneName ]["readonly"]
		return( BooleanEditBone( modulName, boneName, readOnly ) )

	##read
	def unserialize(self, data):
		if self.boneName in data.keys():
			self._setChecked(data[self.boneName])

	##save
	def serializeForPost(self):
		return ( { self.boneName: str(self._getChecked())} )

	##UNUSED
	def serializeForDocument(self):
		return( self.serialize( ) )

def CheckForBooleanBone(  modulName, boneName, skelStucture, *args, **kwargs ):
	return( skelStucture[boneName]["type"]=="bool" )

#Register this Bone in the global queue
editBoneSelector.insert( 3, CheckForBooleanBone, BooleanEditBone)
viewDelegateSelector.insert( 3, CheckForBooleanBone, BooleanViewBoneDelegate)
