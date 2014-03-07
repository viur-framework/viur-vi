#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import html5
from priorityqueue import editBoneSelector, viewDelegateSelector, extendedSearchWidgetSelector
from event import EventDispatcher

class SelectMultiViewBoneDelegate( object ):
	def __init__(self, modulName, boneName, skelStructure, *args, **kwargs ):
		super( SelectMultiViewBoneDelegate, self ).__init__()
		self.skelStructure = skelStructure
		self.boneName = boneName
		self.modulName=modulName

	def render( self, data, field ):
		if field in data.keys():
			result=html5.Ul()
			for fieldKey in data[field]:
				ali=html5.Li()
				if not fieldKey in self.skelStructure[field]["values"].keys():
					ali.appendChild(html5.TextNode(fieldKey))
				else:
					ali.appendChild(html5.TextNode( self.skelStructure[field]["values"][fieldKey] ) )
				ali["Title"] = fieldKey
				result.appendChild(ali)
			return( result)
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
		if self.readOnly:
			self["disabled"] = True


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

class ExtendedSelectMultiSearch( html5.Div ):
	def __init__(self, extension, view, modul, *args, **kwargs ):
		super( ExtendedSelectMultiSearch, self ).__init__( *args, **kwargs )
		self.view = view
		self.extension = extension
		self.modul = modul
		self.filterChangedEvent = EventDispatcher("filterChanged")
		self.appendChild( html5.TextNode("SELECT MULTI SEARCH"))
		self.appendChild( html5.TextNode(extension["name"]))
		self.selectionCb = html5.Select()
		self.appendChild( self.selectionCb )
		o = html5.Option()
		o["value"] = ""
		o.appendChild(html5.TextNode("Ignore"))
		self.selectionCb.appendChild(o)
		for k,v in extension["values"].items():
			o = html5.Option()
			o["value"] = k
			o.appendChild(html5.TextNode(v))
			self.selectionCb.appendChild(o)
		self.sinkEvent("onChange")

	def onChange(self, event):
		event.stopPropagation()
		self.filterChangedEvent.fire()


	def updateFilter(self, filter):
		val = self.selectionCb["options"].item(self.selectionCb["selectedIndex"]).value
		if not val:
			if self.extension["target"] in filter.keys():
				del filter[ self.extension["target"] ]
		else:
			filter[ self.extension["target"] ] = val
		return( filter )

	@staticmethod
	def canHandleExtension( extension, view, modul ):
		return( isinstance( extension, dict) and "type" in extension.keys() and (extension["type"]=="selectmulti" or extension["type"].startswith("selectmulti.") ) )

def CheckForSelectMultiBone(  modulName, boneName, skelStucture, *args, **kwargs ):
	return( skelStucture[boneName]["type"]=="selectmulti" )

#Register this Bone in the global queue
editBoneSelector.insert( 3, CheckForSelectMultiBone, SelectMultiEditBone)
viewDelegateSelector.insert( 3, CheckForSelectMultiBone, SelectMultiViewBoneDelegate)
extendedSearchWidgetSelector.insert( 1, ExtendedSelectMultiSearch.canHandleExtension, ExtendedSelectMultiSearch )
