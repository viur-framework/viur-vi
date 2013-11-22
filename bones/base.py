#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import html5
from priorityqueue import editBoneSelector, viewDelegateSelector


class BaseViewBoneDelegate( object ):
	"""
		Base "Catch-All" delegate for everything not handled separately.
	"""
	def __init__(self, modulName, boneName, skelStructure, *args, **kwargs ):
		super( BaseViewBoneDelegate, self ).__init__()
		self.skelStructure = skelStructure
		self.boneName = boneName
		self.modulName=modulName

	def render( self, data, field ):
		if field in data.keys():
			return( html5.Label(str( data[field])))
		return( html5.Label("..") )

class BaseEditBone( html5.Input ):
	"""
		Base edit widget for everything not handled separately.
	"""
	def setParams(self):
		return
		if self.readOnly:
			self.lineEdit.setReadOnly( True )
		else:
			self.lineEdit.setReadOnly( False )

	def __init__(self, modulName, boneName, readOnly, *args, **kwargs ):
		super( BaseEditBone,  self ).__init__( *args, **kwargs )
		self.boneName = boneName
		self.readOnly = readOnly
		self.setParams()

	@staticmethod
	def fromSkelStructure( modulName, boneName, skelStructure ):
		readOnly = "readonly" in skelStructure[ boneName ].keys() and skelStructure[ boneName ]["readonly"]
		return( BaseEditBone( modulName, boneName, readOnly ) )

	def unserialize(self, data):
		if self.boneName in data.keys():
			self["value"] = data[ self.boneName ] if data[ self.boneName ] else ""
			#self.lineEdit.setText( str( data[ self.boneName ] ) if data[ self.boneName ] else "" )

	def serializeForPost(self):
		return( { self.boneName: self["value"] } )

	def serializeForDocument(self):
		return( self.serialize( ) )


#Register this Bone in the global queue
editBoneSelector.insert( 0, lambda *args, **kwargs: True, BaseEditBone)


viewDelegateSelector.insert( 0, lambda *args, **kwargs: True, BaseViewBoneDelegate)
