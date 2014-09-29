#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import html5
from priorityqueue import editBoneSelector, viewDelegateSelector, extendedSearchWidgetSelector, extractorDelegateSelector
from config import conf
from event import EventDispatcher
from i18n import translate

class BooleanBoneExtractor( object ):
	def __init__(self, modulName, boneName, skelStructure, *args, **kwargs ):
		super( BooleanBoneExtractor, self ).__init__()
		self.skelStructure = skelStructure
		self.boneName = boneName
		self.modulName = modulName

	def render( self, data, field ):
		if field in data.keys():
			return str( data[field])
		return ".."


class BooleanViewBoneDelegate( object ):
	def __init__(self, modulName, boneName, skelStructure, *args, **kwargs ):
		super( BooleanViewBoneDelegate, self ).__init__()
		self.skelStructure = skelStructure
		self.boneName = boneName
		self.modulName = modulName

	def render( self, data, field ):
		if field in data.keys():
			return( html5.Label(str( data[field])))
		return( html5.Label("..") )

class BooleanEditBone( html5.Input ):

	def __init__(self, modulName, boneName,readOnly, *args, **kwargs ):
		super( BooleanEditBone,  self ).__init__( *args, **kwargs )
		self.boneName = boneName
		self.readOnly = readOnly
		self["type"]="checkbox"
		if readOnly:
			self["disabled"]=True


	@staticmethod
	def fromSkelStructure( modulName, boneName, skelStructure ):
		readOnly = "readonly" in skelStructure[ boneName ].keys() and skelStructure[ boneName ]["readonly"]
		return( BooleanEditBone( modulName, boneName, readOnly ) )

	##read
	def unserialize(self, data, extendedErrorInformation=None):
		if self.boneName in data.keys():
			self._setChecked(data[self.boneName])

	##save
	def serializeForPost(self):
		return ( { self.boneName: str(self._getChecked())} )

	##UNUSED
	def serializeForDocument(self):
		return( self.serialize( ) )


class ExtendedBooleanSearch( html5.Div ):
	def __init__(self, extension, view, modul, *args, **kwargs ):
		super( ExtendedBooleanSearch, self ).__init__( *args, **kwargs )
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
		o = html5.Option()
		o["value"] = "0"
		o.appendChild(html5.TextNode(translate("No")))
		self.selectionCb.appendChild(o)
		o = html5.Option()
		o["value"] = "1"
		o.appendChild(html5.TextNode(translate("Yes")))
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
		return( isinstance( extension, dict) and "type" in extension.keys() and (extension["type"]=="boolean" or extension["type"].startswith("boolean.") ) )



def CheckForBooleanBone(  modulName, boneName, skelStucture, *args, **kwargs ):
	return( skelStucture[boneName]["type"]=="bool" )

#Register this Bone in the global queue
editBoneSelector.insert( 3, CheckForBooleanBone, BooleanEditBone)
viewDelegateSelector.insert( 3, CheckForBooleanBone, BooleanViewBoneDelegate)
extendedSearchWidgetSelector.insert( 1, ExtendedBooleanSearch.canHandleExtension, ExtendedBooleanSearch )
extractorDelegateSelector.insert(3, CheckForBooleanBone, BooleanBoneExtractor)
