#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import html5
from priorityqueue import editBoneSelector, viewDelegateSelector
from config import conf

class StringViewBoneDelegate( object ):
	def __init__(self, modulName, boneName, skelStructure, *args, **kwargs ):
		super( StringViewBoneDelegate, self ).__init__()
		self.skelStructure = skelStructure
		self.boneName = boneName
		self.modulName=modulName

	def render( self, data, field ):
		if field in data.keys():
			##multilangs
			if isinstance(data[field],dict):
				resstr=""
				if "currentlanguage" in conf.keys():
					if conf["currentlanguage"] in data[field].keys():
						resstr=data[field][conf["currentlanguage"]]
					else:
						if data[field].keys().length>0:
							resstr=data[field][data[field].keys()[0]]
				aspan=html5.Span()
				aspan.appendChild(html5.TextNode(resstr))
				aspan["Title"]=str( data[field])
				return (resstr)
			else:
				return( html5.Label(str( data[field])))
		return( html5.Label("..") )

class StringEditBone( html5.Input ):

	def __init__(self, modulName, boneName,readOnly, *args, **kwargs ):
		super( StringEditBone,  self ).__init__( *args, **kwargs )
		self.boneName = boneName
		self.readOnly = readOnly
		if readOnly:
			self["disabled"]=True

	@staticmethod
	def fromSkelStructure( modulName, boneName, skelStructure ):
		readOnly = "readonly" in skelStructure[ boneName ].keys() and skelStructure[ boneName ]["readonly"]
		return( StringEditBone( modulName, boneName, readOnly ) )

	def unserialize(self, data):
		if self.boneName in data.keys():
			self["value"] = data[ self.boneName ] if data[ self.boneName ] else ""

	def serializeForPost(self):
			return( { self.boneName: self["value"] } )

	def serializeForDocument(self):
		return( self.serialize( ) )

def CheckForStringBone(  modulName, boneName, skelStucture ):
	return( skelStucture[boneName]["type"]=="string" )

#Register this Bone in the global queue
editBoneSelector.insert( 3, CheckForStringBone, StringEditBone)
viewDelegateSelector.insert( 3, CheckForStringBone, StringViewBoneDelegate)
