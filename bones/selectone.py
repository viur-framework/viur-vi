#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import html5
from priorityqueue import editBoneSelector, viewDelegateSelector

class SelectOneViewBoneDelegate( object ):
	def __init__(self, modulName, boneName, skelStructure, *args, **kwargs ):
		super( SelectOneViewBoneDelegate, self ).__init__()
		self.skelStructure = skelStructure
		self.boneName = boneName
		self.modulName=modulName

	def render( self, data, field ):
		if field in data.keys():
			aspan=html5.Span()
			aspan.appendChild(html5.TextNode(self.skelStructure[field]["values"][data[field]]))
			aspan["Title"]=data[field]
			return(aspan)
		return( html5.Label("..") )

class SelectOneEditBone( html5.Select ):

	def __init__(self, modulName, boneName,readOnly,values, *args, **kwargs ):
		super( SelectOneEditBone,  self ).__init__( *args, **kwargs )
		self.boneName = boneName
		self["name"]=boneName
		self.readOnly = readOnly
		self.values=values
		for key, value in values.items():
			aoption=html5.Option()
			aoption["value"]=key
			aoption.element.innerHTML=value
			self.appendChild(aoption)


	@staticmethod
	def fromSkelStructure( modulName, boneName, skelStructure ):
		readOnly = "readonly" in skelStructure[ boneName ].keys() and skelStructure[ boneName ]["readonly"]
		if "values" in skelStructure[ boneName ].keys():
			values =skelStructure[ boneName ]["values"]
		else:
			values = {}
		return( SelectOneEditBone( modulName, boneName, readOnly,values ) )

	def unserialize(self, data):
		if self.boneName in data.keys():
			self.val = data[ self.boneName ] if data[ self.boneName ] else ""
			for aoption in self._children:
				if aoption["value"] == self.val:
					aoption["selected"]=True

	def serializeForPost(self):
			for aoption in self._children:
				if aoption["selected"]:
					return( { self.boneName: aoption["value"] } )
			return ({})

	def serializeForDocument(self):
		return( self.serialize( ) )

def CheckForSelectOneBone(  modulName, boneName, skelStucture, *args, **kwargs ):
	return( skelStucture[boneName]["type"]=="selectone" )

#Register this Bone in the global queue
editBoneSelector.insert( 3, CheckForSelectOneBone, SelectOneEditBone)
viewDelegateSelector.insert( 3, CheckForSelectOneBone, SelectOneViewBoneDelegate)
