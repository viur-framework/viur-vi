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
		print(self.skelStructure[field]["values"])
		if field in data.keys():
			resul=html5.Ul()

			for d in data[field]:

				ali=html5.Li()
				ali.element.innerHTML=self.skelStructure[field]["values"][d]
				ali["Title"]=d
				resul.appendChild(ali)
			return( resul)
		return( html5.Label("&nbsp; - &nbsp;") )

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
		if self.boneName in data.keys():
			self.val = data[ self.boneName ] if data[ self.boneName ] else []
			for alabel in self._children:
				if alabel._children[0]["name"] in self.val:
					alabel._children[0]["checked"]=True

	def serializeForPost(self):
		value=[]
		for alabel in self._children:
			if alabel._children[0]["checked"]:
				value.append(alabel._children[0]["name"])
		return( { self.boneName: value } )

	def serializeForDocument(self):
		return( self.serialize( ) )

def CheckForSelectMultiBone(  modulName, boneName, skelStucture ):
	return( skelStucture[boneName]["type"]=="selectmulti" )

#Register this Bone in the global queue
editBoneSelector.insert( 3, CheckForSelectMultiBone, SelectMultiEditBone)
viewDelegateSelector.insert( 3, CheckForSelectMultiBone, SelectMultiViewBoneDelegate)
