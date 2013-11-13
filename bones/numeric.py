#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import html5
from priorityqueue import editBoneSelector, viewDelegateSelector

class NumericViewBoneDelegate( object ):
	def __init__(self, modulName, boneName, skelStructure, *args, **kwargs ):
		super( NumericViewBoneDelegate, self ).__init__()
		self.skelStructure = skelStructure
		self.boneName = boneName
		self.modulName=modulName

	def render( self, data, field ):
		if field in data.keys():
			return( html5.Label(str( data[field])))
		return( html5.Label("..") )

class NumericEditBone( html5.Input ):
	def __init__(self, modulName, boneName,readOnly,_min=False,_max=False,precision=False, *args, **kwargs ):
		super( NumericEditBone,  self ).__init__( *args, **kwargs )
		self.boneName = boneName
		self.readOnly = readOnly
		self["type"]="number"
		if _min:
			self["min"]=_min
		if _max:
			self["max"]=_max
		if precision:
			self["step"]=precision

	@staticmethod
	def fromSkelStructure( modulName, boneName, skelStructure ):
		readOnly = "readonly" in skelStructure[ boneName ].keys() and skelStructure[ boneName ]["readonly"]
		if "params" in skelStructure[ boneName ].keys():
			_min=skelStructure[ boneName ]["params"]["min"] if "min" in skelStructure[ boneName ]["params"].keys() else False
			_max=skelStructure[ boneName ]["params"]["max"] if "max" in skelStructure[ boneName ]["params"].keys() else False
			precision=skelStructure[ boneName ]["params"]["precision"] if "precision" in skelStructure[ boneName ]["params"].keys() else False
			return( NumericEditBone( modulName, boneName, readOnly,_min,_max,precision ) )
		return( NumericEditBone( modulName, boneName, readOnly ) )

	def unserialize(self, data):
		if self.boneName in data.keys():
			self["value"] = data[ self.boneName ] if data[ self.boneName ] else ""

	def serializeForPost(self):
		return( { self.boneName: self["value"] } )

	def serializeForDocument(self):
		return( self.serialize( ) )

def CheckForNumericBone(  modulName, boneName, skelStucture ):
	return( skelStucture[boneName]["type"]=="numeric" )

#Register this Bone in the global queue
editBoneSelector.insert( 3, CheckForNumericBone, NumericEditBone)
viewDelegateSelector.insert( 3, CheckForNumericBone, NumericViewBoneDelegate)
