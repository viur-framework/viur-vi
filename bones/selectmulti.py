#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import html5
from priorityqueue import editBoneSelector, viewDelegateSelector

class SelectMultiViewBoneDelegate( object ):
	def __init__(self, modulName, boneName, skelStructure, *args, **kwargs ):
		super( SelectMultiViewBoneDelegate, self ).__init__()
		self.skelStructure = skelStructure
		self.boneName = boneName
		self.modulName=modulName

	def render( self, data, field ):
		if field in data.keys():
			return( html5.Label(str( data[field])))
		return( html5.Label("..") )

class SelectMultiEditBone( html5.Div ):

	def __init__(self, modulName, boneName,readOnly,values, *args, **kwargs ):
		super( SelectMultiEditBone,  self ).__init__( *args, **kwargs )
		self.boneName = boneName
		self.readOnly = readOnly
		self.values=values
		for key, value in values.items():
			alabel=html5.Label()
			acheckbox=html5.Input()
			acheckbox["type"]="checkbox"
			acheckbox["name"]=key
			alabel.appendChild(acheckbox)
			aspan=html5.Span()
			aspan.element.innerHTML=value
			alabel.appendChild(aspan)
			self.appendChild(alabel)


	@staticmethod
	def fromSkelStructure( modulName, boneName, skelStructure ):
		readOnly = "readonly" in skelStructure[ boneName ].keys() and skelStructure[ boneName ]["readonly"]
		if "values" in skelStructure[ boneName ].keys():
			values =skelStructure[ boneName ]["values"]
		else:
			values = {}
		return( SelectMultiEditBone( modulName, boneName, readOnly,values ) )

	def unserialize(self, data):
		return
		if self.boneName in data.keys():
			self["value"] = data[ self.boneName ] if data[ self.boneName ] else ""
			#self.lineEdit.setText( str( data[ self.boneName ] ) if data[ self.boneName ] else "" )

	def serializeForPost(self):
		return( { self.boneName: self["value"] } )

	def serializeForDocument(self):
		return( self.serialize( ) )

def CheckForSelectMultiBone(  modulName, boneName, skelStucture ):
	return( skelStucture[boneName]["type"]=="selectmulti" )

#Register this Bone in the global queue
editBoneSelector.insert( 3, CheckForSelectMultiBone, SelectMultiEditBone)
viewDelegateSelector.insert( 3, CheckForSelectMultiBone, SelectMultiViewBoneDelegate)
