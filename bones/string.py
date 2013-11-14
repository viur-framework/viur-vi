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
						if len(data[field].keys())>0:
							resstr=data[field][data[field].keys()[0]]
				aspan=html5.Span()
				aspan.appendChild(html5.TextNode(resstr))
				aspan["Title"]=str( data[field])
				return (aspan)
			else:
				#no langobject
				return( html5.Label(str( data[field])))
		return( html5.Label("..") )

class StringEditBone( html5.Div ):
	def __init__(self, modulName, boneName,readOnly,skelStructure=False,*args, **kwargs ):
		super( StringEditBone,  self ).__init__( *args, **kwargs )
		self.boneName = boneName
		self.readOnly = readOnly
		self.selectedLang=False
		self.skelStructure=skelStructure
		##multilangbone
		if skelStructure and skelStructure[boneName]["languages"]:
			if "currentlanguage" in conf and conf["currentlanguage"] in skelStructure[boneName]["languages"]:
				self.selectedLang=conf["currentlanguage"]
			elif len(skelStructure[boneName]["languages"])>0:
				self.selectedLang=skelStructure[boneName]["languages"][0]
			self.langButContainer=html5.Div()
			for lang in skelStructure[boneName]["languages"]:
				abut=html5.ext.Button(lang,self.changeLang)
				abut["value"]=lang
				self.langButContainer.appendChild(abut)
			self.appendChild(self.langButContainer)
			self.refreshLangButContainer()
		self.input=html5.Input()
		self.setSpecialType()
		if readOnly:
			self.input["disabled"]=True
		self.appendChild(self.input)

	def changeLang(self,btn):
		if "data" in self.keys():
			self.data[self.selectedLang]=self.input["value"]
			self.selectedLang=btn["value"]
			self.input["value"]=self.data[self.selectedLang]
			self.refreshLangButContainer()

	def refreshLangButContainer(self):
		return ()
		for abut in self.langButContainer["children"]:
			if abut["value"]==self.selectedLang:
				abut["class"].append("is_active")
			else:
				abut["class"].remove("is_active")

	def setSpecialType(self):
		pass
	  #emailbone may set self.input["type"]="email"

	@staticmethod
	def fromSkelStructure( modulName, boneName, skelStructure ):
		readOnly = "readonly" in skelStructure[ boneName ].keys() and skelStructure[ boneName ]["readonly"]
		return( StringEditBone( modulName, boneName, readOnly,skelStructure ) )

	def unserialize(self, data):
		self.data=False
		if self.boneName in data.keys():
			self.data=data
			if isinstance(self.data[self.boneName],dict) and self.selectedLang:
				self.input["value"] = self.data[ self.boneName ][self.selectedLang] if self.selectedLang in self.data[ self.boneName].keys() else ""
			else:
				self.input["value"] = self.data[ self.boneName ] if self.data[ self.boneName ] else ""

	def serializeForPost(self):
		if self.selectedLang:
			self.data[self.selectedLang]=self.input["value"]
			return( { self.boneName: self.data } )
		else:
			return( { self.boneName: self.input["value"] } )

	def serializeForDocument(self):
		return( self.serialize( ) )

def CheckForStringBone(  modulName, boneName, skelStucture ):
	return( skelStucture[boneName]["type"]=="str" )

#Register this Bone in the global queue
editBoneSelector.insert( 3, CheckForStringBone, StringEditBone)
viewDelegateSelector.insert( 3, CheckForStringBone, StringViewBoneDelegate)
