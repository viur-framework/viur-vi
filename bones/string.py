#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import html5
from priorityqueue import editBoneSelector, viewDelegateSelector, extendedSearchWidgetSelector
from config import conf
from event import EventDispatcher
from html5.keycodes import *
from i18n import translate

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
				return (self.getViewElement(resstr,data[field]))


			else:
				#no langobject
				return (self.getViewElement(str( data[field]),False))
		return (self.getViewElement("..",False))

	def getViewElement(self,labelstr,datafield):
		if not datafield:
			return( html5.Label(labelstr))
		else:
			aspan=html5.Span()
			aspan.appendChild(html5.TextNode(labelstr))
			aspan["Title"]=str(datafield)
			return (aspan)

def unescapeHtml( html ): #FIXME!
	return( html )

class Tag( html5.Span ):
	def __init__(self, tag, isEditMode, *args, **kwargs ):
		super( Tag, self ).__init__( *args, **kwargs )
		self["class"].append("tag")
		self.input = html5.Input()
		self.input["type"] = "text"
		self.input["value"] = tag
		self.appendChild(self.input)
		delBtn = html5.ext.Button(translate("Delete"), self.removeMe)
		delBtn["class"].append("icon delete tag")
		self.appendChild(delBtn)

	def removeMe(self, *args, **kwargs):
		self.parent().removeChild( self )



class StringEditBone( html5.Div ):
	def __init__(self, modulName, boneName, readOnly, multiple=False, languages=None, *args, **kwargs ):
		super( StringEditBone,  self ).__init__( *args, **kwargs )
		self.modulName = modulName
		self.boneName = boneName
		self.readOnly = readOnly
		self.multiple = multiple
		self.languages = languages
		self.boneName = boneName
		self.currentLanguage = None
		if self.languages and self.multiple:
			self["class"].append("is_translated")
			self["class"].append("is_multiple")
			self.languagesContainer = html5.Div()
			self.appendChild( self.languagesContainer )
			self.buttonContainer = html5.Div()
			self.buttonContainer["class"] = "languagebuttons"
			self.appendChild( self.buttonContainer )
			self.langEdits = {}
			for lang in self.languages:
				tagContainer = html5.Div()
				tagContainer["class"].append("lang_%s" % lang )
				tagContainer["class"].append("tagcontainer")
				tagContainer["style"]["display"] = "none"
				btn = html5.ext.Button(lang, callback=self.onLangBtnClicked)
				btn.lang = lang
				self.buttonContainer.appendChild( btn )
				addBtn = html5.ext.Button(translate("New"), callback=self.onBtnGenTag)
				addBtn["class"].append("icon new tag")
				addBtn.lang = lang
				tagContainer.appendChild(addBtn)
				self.languagesContainer.appendChild(tagContainer)
				self.langEdits[lang] = tagContainer
			self.setLang(self.languages[0])
		elif self.languages and not self.multiple:
			self["class"].append("is_translated")
			self.languagesContainer = html5.Div()
			self.appendChild( self.languagesContainer )
			self.buttonContainer = html5.Div()
			self.buttonContainer["class"] = "languagebuttons"
			self.appendChild( self.buttonContainer )
			self.langEdits = {}
			for lang in self.languages:
				btn = html5.ext.Button(lang, callback=self.onLangBtnClicked)
				btn.lang = lang
				self.buttonContainer.appendChild( btn )
				inputField = html5.Input()
				inputField["type"] = "text"
				inputField["style"]["display"] = "none"
				inputField["class"].append("lang_%s" % lang)
				self.languagesContainer.appendChild( inputField )
				self.langEdits[lang] = inputField
			self.setLang(self.languages[0])
		elif not self.languages and self.multiple:
			self["class"].append("is_multiple")
			self.tagContainer = html5.Div()
			self.tagContainer["class"].append("tagcontainer")
			self.appendChild(self.tagContainer)
			addBtn = html5.ext.Button(translate("New"), callback=self.onBtnGenTag)
			addBtn.lang = None
			addBtn["class"].append("icon new tag")
			self.tagContainer.appendChild(addBtn)
		else: #not languages and not multiple:
			self.input = html5.Input()
			self.input["type"] = "text"
			self.appendChild( self.input )
		if self.readOnly:
			self["disabled"] = True

	@staticmethod
	def fromSkelStructure( modulName, boneName, skelStructure ):
		readOnly = "readonly" in skelStructure[ boneName ].keys() and skelStructure[ boneName ]["readonly"]
		if boneName in skelStructure.keys():
			if "multiple" in skelStructure[ boneName ].keys():
				multiple = skelStructure[ boneName ]["multiple"]
			else:
				multiple = False
			if "languages" in skelStructure[ boneName ].keys():
				languages = skelStructure[ boneName ]["languages"]
			else:
				languages = None
		return( StringEditBone( modulName, boneName, readOnly, multiple=multiple, languages=languages ) )


	def onLangBtnClicked(self, btn):
		self.setLang( btn.lang )

	def setLang(self, lang):
		if self.currentLanguage:
			self.langEdits[ self.currentLanguage ]["style"]["display"] = "none"
		self.currentLanguage = lang
		self.langEdits[ self.currentLanguage ]["style"]["display"] = ""

	def onBtnGenTag(self, btn):
		self.genTag( "", lang=btn.lang )


	def unserialize( self, data, extendedErrorInformation=None ):
		if not self.boneName in data.keys():
			return
		data = data[ self.boneName ]
		if not data:
			return
		if self.languages and self.multiple:
			assert isinstance(data,dict)
			for lang in self.languages:
				if lang in data.keys():
					val = data[ lang ]
					if isinstance( val, str ):
						self.genTag( unescapeHtml(val), lang=lang )
					elif isinstance( val, list ):
						for v in val:
							self.genTag( unescapeHtml(v), lang=lang )
		elif self.languages and not self.multiple:
			assert isinstance(data,dict)
			for lang in self.languages:
				if lang in data.keys() and data[ lang ]:
					self.langEdits[ lang ]["value"] = unescapeHtml(str(data[ lang ]))
				else:
					self.langEdits[ lang ]["value"] = ""
		elif not self.languages and self.multiple:
			if isinstance( data,list ):
				for tagStr in data:
					self.genTag( unescapeHtml(tagStr) )
			else:
				self.genTag( unescapeHtml(data) )
		else:
			self.input["value"] = unescapeHtml(str(data))

	def serializeForPost(self):
		res = {}
		if self.languages and self.multiple:
			for lang in self.languages:
				res[ "%s.%s" % (self.boneName, lang ) ] = []
				for child in self.langEdits[ lang ]._children:
					if isinstance( child, Tag ):
						res[ "%s.%s" % (self.boneName, lang ) ].append( child.input["value"] )
		elif self.languages and not self.multiple:
			for lang in self.languages:
				txt = self.langEdits[ lang ]["value"]
				if txt:
					res[ "%s.%s" % (self.boneName, lang) ] = txt
		elif not self.languages and self.multiple:
			res[ self.boneName ] = []
			for child in self.tagContainer._children:
				if isinstance( child, Tag ):
					res[ self.boneName ].append( child.input["value"] )
		elif not self.languages and not self.multiple:
			res[ self.boneName ] = self.input["value"]
		return( res )

	def serializeForDocument(self):
		return( self.serialize( ) )

	def genTag( self, tag, editMode=False, lang=None ):
		tag =  Tag( tag, editMode )
		if lang is not None:
			self.langEdits[ lang ].appendChild( tag )
		else:
			self.tagContainer.appendChild( tag )



def CheckForStringBone(  modulName, boneName, skelStucture, *args, **kwargs ):
	return( str(skelStucture[boneName]["type"]).startswith("str") )


class ExtendedStringSearch( html5.Div ):
	def __init__(self, extension, view, modul, *args, **kwargs ):
		super( ExtendedStringSearch, self ).__init__( *args, **kwargs )
		self.view = view
		self.extension = extension
		self.modul = modul
		self.opMode = extension["mode"]
		self.filterChangedEvent = EventDispatcher("filterChanged")
		assert self.opMode in ["equals","from", "to", "prefix","range"]
		self.appendChild( html5.TextNode(extension["name"]))
		self.sinkEvent("onKeyDown")
		if self.opMode in ["equals","from", "to", "prefix"]:
			self.input = html5.Input()
			self.input["type"] = "text"
			self.appendChild( self.input )
		elif self.opMode == "range":
			self.input1 = html5.Input()
			self.input1["type"] = "text"
			self.appendChild( self.input1 )
			self.appendChild( html5.TextNode("to") )
			self.input2 = html5.Input()
			self.input2["type"] = "text"
			self.appendChild( self.input2 )

	def onKeyDown(self, event):
		if isReturn(event.keyCode):
			self.filterChangedEvent.fire()

	def updateFilter(self, filter):
		if self.opMode=="equals":
			filter[ self.extension["target"] ] = self.input["value"]
		elif self.opMode=="from":
			filter[ self.extension["target"]+"$gt" ] = self.input["value"]
		elif self.opMode=="to":
			filter[ self.extension["target"]+"$lt" ] = self.input["value"]
		elif self.opMode=="prefix":
			filter[ self.extension["target"]+"$lk" ] = self.input["value"]
		elif self.opMode=="range":
			filter[ self.extension["target"]+"$gt" ] = self.input1["value"]
			filter[ self.extension["target"]+"$lt" ] = self.input2["value"]
		return( filter )

	@staticmethod
	def canHandleExtension( extension, view, modul ):
		return( isinstance( extension, dict) and "type" in extension.keys() and (extension["type"]=="string" or extension["type"].startswith("string.") ) )


#Register this Bone in the global queue
editBoneSelector.insert( 3, CheckForStringBone, StringEditBone)
viewDelegateSelector.insert( 3, CheckForStringBone, StringViewBoneDelegate)
extendedSearchWidgetSelector.insert( 1, ExtendedStringSearch.canHandleExtension, ExtendedStringSearch )
