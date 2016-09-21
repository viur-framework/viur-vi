#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import html5
from priorityqueue import editBoneSelector, viewDelegateSelector, extractorDelegateSelector
from config import conf


class BaseBoneExtractor( object ):
	def __init__(self, moduleName, boneName, skelStructure, *args, **kwargs):
		super(BaseBoneExtractor, self).__init__()
		self.skelStructure = skelStructure
		self.boneName = boneName
		self.moduleName=moduleName

	def render( self, data, field ):
		if field in data.keys():
			return str(data[field])
		return conf["empty_value"]


class BaseViewBoneDelegate( object ):
	"""
		Base "Catch-All" delegate for everything not handled separately.
	"""
	def __init__(self, moduleName, boneName, skelStructure, *args, **kwargs ):
		super( BaseViewBoneDelegate, self ).__init__()
		self.skelStructure = skelStructure
		self.boneName = boneName
		self.moduleName=moduleName

	def render( self, data, field ):
		if field in data.keys():
			return( html5.Label(str( data[field])))
		return( html5.Label( conf[ "empty_value" ] ) )


class BaseEditBone( html5.Input ):
	"""
		Base edit widget for everything not handled separately.
	"""
	def setParams(self):
		if self.readOnly:
			self["disabled"] = True

	def __init__(self, moduleName, boneName, readOnly, *args, **kwargs ):
		super( BaseEditBone,  self ).__init__( *args, **kwargs )
		self.boneName = boneName
		self.readOnly = readOnly
		self.setParams()

	@staticmethod
	def fromSkelStructure( moduleName, boneName, skelStructure ):
		readOnly = "readonly" in skelStructure[ boneName ].keys() and skelStructure[ boneName ]["readonly"]
		return( BaseEditBone( moduleName, boneName, readOnly ) )

	def unserialize(self, data, extendedErrorInformation=None):
		if self.boneName in data.keys():
			self["value"] = data[ self.boneName ] if data[ self.boneName ] else ""
			#self.lineEdit.setText( str( data[ self.boneName ] ) if data[ self.boneName ] else "" )

	def serializeForPost(self):
		return( { self.boneName: self["value"] } )

	def serializeForDocument(self):
		return( self.serialize( ) )

	def setExtendedErrorInformation(self, errorInfo ):
		pass




def CheckForBaseBone(moduleName, boneName, skelStucture, *args, **kwargs):
	res = str(skelStucture[boneName]["type"]).startswith("hidden")
	print("checking basebone", str(skelStucture[boneName]["type"]), res)
	return res


#Register this Bone in the global queue
editBoneSelector.insert( 0, lambda *args, **kwargs: True, BaseEditBone)


viewDelegateSelector.insert( 0, lambda *args, **kwargs: True, BaseViewBoneDelegate)
extractorDelegateSelector.insert(0, CheckForBaseBone, BaseBoneExtractor)
