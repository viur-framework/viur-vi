#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import html5
from priorityqueue import editBoneSelector, viewDelegateSelector, extendedSearchWidgetSelector
from event import EventDispatcher
from i18n import translate
class SelectOneViewBoneDelegate( object ):
	def __init__(self, modulName, boneName, skelStructure, *args, **kwargs ):
		super( SelectOneViewBoneDelegate, self ).__init__()
		self.skelStructure = skelStructure
		self.boneName = boneName
		self.modulName=modulName

	def render( self, data, field ):
		if field in data.keys():
			aspan=html5.Span()
			if data and field and field in self.skelStructure and data[field] and data[field] in self.skelStructure[field]["values"]:
				aspan.appendChild(html5.TextNode(self.skelStructure[field]["values"][data[field]]))
				aspan["Title"]=data[field]
				return(aspan)
		return( html5.Label("..") )

class SelectOneEditBone( html5.Select ):

	def __init__(self, modulName, boneName, readOnly, values, sortBy="keys", *args, **kwargs ):
		super( SelectOneEditBone,  self ).__init__( *args, **kwargs )
		self.boneName = boneName
		self["name"]=boneName
		self.readOnly = readOnly
		self.values=values
		tmpList = values.items()
		if sortBy=="keys":
			tmpList.sort( key=lambda x: x[0] ) #Sort by keys
		else:
			tmpList.sort( key=lambda x: x[1] ) #Values
		for key, value in tmpList:
			aoption=html5.Option()
			aoption["value"]=key
			aoption.element.innerHTML=value
			self.appendChild(aoption)
		if self.readOnly:
			self["disabled"] = True


	@staticmethod
	def fromSkelStructure( modulName, boneName, skelStructure ):
		readOnly = "readonly" in skelStructure[ boneName ].keys() and skelStructure[ boneName ]["readonly"]
		if "sortBy" in skelStructure[ boneName ].keys():
			sortBy = skelStructure[ boneName ][ "sortBy" ]
		else:
			sortBy = "keys"
		if "values" in skelStructure[ boneName ].keys():
			values =skelStructure[ boneName ]["values"]
		else:
			values = {}
		return( SelectOneEditBone( modulName, boneName, readOnly, values, sortBy ) )

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

class ExtendedSelectOneSearch( html5.Div ):
	def __init__(self, extension, view, modul, *args, **kwargs ):
		super( ExtendedSelectOneSearch, self ).__init__( *args, **kwargs )
		self.view = view
		self.extension = extension
		self.modul = modul
		self.filterChangedEvent = EventDispatcher("filterChanged")
		self.appendChild( html5.TextNode(extension["name"]))
		self.selectionCb = html5.Select()
		self.appendChild( self.selectionCb )
		o = html5.Option()
		o["value"] = ""
		o.appendChild(html5.TextNode(translate("Ignore")))
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
		return( isinstance( extension, dict) and "type" in extension.keys() and (extension["type"]=="selectone" or extension["type"].startswith("selectone.") ) )

def CheckForSelectOneBone(  modulName, boneName, skelStucture, *args, **kwargs ):
	return( skelStucture[boneName]["type"]=="selectone" )

#Register this Bone in the global queue
editBoneSelector.insert( 3, CheckForSelectOneBone, SelectOneEditBone)
viewDelegateSelector.insert( 3, CheckForSelectOneBone, SelectOneViewBoneDelegate)
extendedSearchWidgetSelector.insert( 1, ExtendedSelectOneSearch.canHandleExtension, ExtendedSelectOneSearch )
