#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import html5
from priorityqueue import editBoneSelector, viewDelegateSelector
from config import conf

class ColorViewBoneDelegate( object ):
	def __init__(self, modulName, boneName, skelStructure, *args, **kwargs ):
		super( ColorViewBoneDelegate, self ).__init__()
		self.skelStructure = skelStructure
		self.boneName = boneName
		self.modulName = modulName

	def render( self, data, field ):
		if field in data.keys():
			can = html5.Div()
			can["style"]["width"]="60px"
			adiv = html5.Div()
			adiv["style"]["width"]="10px"
			adiv["style"]["height"]="10px"
			adiv["style"]["background-Color"]=str( data[field])
			adiv["style"]["float"]="left"
			adiv["style"]["margin-top"]="6px"
			adiv["style"]["margin-right"]="3px"

			lbl = html5.Label(str( data[field]))
			can.appendChild(adiv)
			can.appendChild(lbl)
			return(can)
		return( html5.Label("..") )

class ColorEditBone( html5.Input ):

	def __init__(self, modulName, boneName,readOnly, *args, **kwargs ):
		super( ColorEditBone,  self ).__init__( *args, **kwargs )
		self.boneName = boneName
		self.readOnly = readOnly
		self["type"]="color"
		if readOnly:
			self["disabled"]=True


	@staticmethod
	def fromSkelStructure( modulName, boneName, skelStructure ):
		readOnly = "readonly" in skelStructure[ boneName ].keys() and skelStructure[ boneName ]["readonly"]
		return( ColorEditBone( modulName, boneName, readOnly ) )

	##read
	def unserialize(self, data):
		if self.boneName in data.keys():
			self._setValue(data[self.boneName])

	##save
	def serializeForPost(self):
		return ( { self.boneName: str(self._getValue())} )

	##UNUSED
	def serializeForDocument(self):
		return( self.serialize( ) )

def CheckForColorBone(  modulName, boneName, skelStucture ):
	return( skelStucture[boneName]["type"]=="color" )

#Register this Bone in the global queue
editBoneSelector.insert( 3, CheckForColorBone, ColorEditBone)
viewDelegateSelector.insert( 3, CheckForColorBone, ColorViewBoneDelegate)
