#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import html5
from priorityqueue import editBoneSelector, viewDelegateSelector

class PasswordEditBone( html5.Div ):
	def __init__(self, modulName, boneName, readOnly, *args, **kwargs ):
		super( PasswordEditBone,  self ).__init__( *args, **kwargs )
		self.boneName = boneName
		self.readOnly = readOnly
		self.setParams()
		self.primeinput=html5.Input()
		self.secondinput=html5.Input()
		self.primeinput["type"]="password"
		self.secondinput["type"]="password"
		self.appendChild(self.primeinput)
		lbl=html5.Label("reenter password")
		lbl["for"]==modulName+"_"+boneName+"_reenterpwd"
		self.appendChild(lbl)
		self.secondinput["name"]=modulName+"_"+boneName+"_reenterpwd"
		self.appendChild(self.secondinput)


	@staticmethod
	def fromSkelStructure( modulName, boneName, skelStructure ):
		readOnly = "readonly" in skelStructure[ boneName ].keys() and skelStructure[ boneName ]["readonly"]
		return( PasswordEditBone( modulName, boneName, readOnly ) )

	def unserialize(self, data):
		if self.boneName in data.keys():
			self["value"] = data[ self.boneName ] if data[ self.boneName ] else ""
			#self.lineEdit.setText( str( data[ self.boneName ] ) if data[ self.boneName ] else "" )

	def serializeForPost(self):
		return( { self.boneName: self["value"] } )

	def serializeForDocument(self):
		return( self.serialize( ) )

def CheckForPasswordBone(  modulName, boneName, skelStucture ):
	return( str(skelStucture[boneName]["type"]).startswith("password") )


#Register this Bone in the global queue
editBoneSelector.insert( 3, CheckForPasswordBone, PasswordEditBone)


