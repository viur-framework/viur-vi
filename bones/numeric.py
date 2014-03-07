#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import html5
from priorityqueue import editBoneSelector, viewDelegateSelector, extendedSearchWidgetSelector
from event import EventDispatcher
from html5.keycodes import *

class NumericViewBoneDelegate( object ):
	def __init__(self, modulName, boneName, skelStructure, *args, **kwargs ):
		super( NumericViewBoneDelegate, self ).__init__()
		self.skelStructure = skelStructure
		self.boneName = boneName
		self.modulName=modulName

	def render( self, data, field ):
		if field in data.keys():
			return( html5.Label(str( data[field])))
		return( html5.Label("..") )

class NumericEditBone( html5.Input ):
	def __init__(self, modulName, boneName,readOnly,_min=False,_max=False,precision=False, *args, **kwargs ):
		super( NumericEditBone,  self ).__init__( *args, **kwargs )
		self.boneName = boneName
		self.readOnly = readOnly
		self["type"]="number"
		if _min:
			self["min"]=_min
		if _max:
			self["max"]=_max
		if precision:
			self["step"]=precision
		if self.readOnly:
			self["disabled"] = True

	@staticmethod
	def fromSkelStructure( modulName, boneName, skelStructure ):
		readOnly = "readonly" in skelStructure[ boneName ].keys() and skelStructure[ boneName ]["readonly"]
		if "params" in skelStructure[ boneName ].keys():
			_min=skelStructure[ boneName ]["params"]["min"] if (isinstance(skelStructure[ boneName ]["params"],dict) and "min" in skelStructure[ boneName ]["params"].keys()) else False
			_max=skelStructure[ boneName ]["params"]["max"] if (isinstance(skelStructure[ boneName ]["params"],dict) and "max" in skelStructure[ boneName ]["params"].keys()) else False
			precision=skelStructure[ boneName ]["params"]["precision"] if (isinstance(skelStructure[ boneName ]["params"],dict) and "precision" in skelStructure[ boneName ]["params"].keys()) else False
			return( NumericEditBone( modulName, boneName, readOnly,_min,_max,precision ) )
		return( NumericEditBone( modulName, boneName, readOnly ) )

	def unserialize(self, data):
		if self.boneName in data.keys():
			self["value"] = data[ self.boneName ] if data[ self.boneName ] else ""

	def serializeForPost(self):
		return( { self.boneName: self["value"] } )

	def serializeForDocument(self):
		return( self.serialize( ) )

	def setExtendedErrorInformation(self, errorInfo ):
		pass


class ExtendedNumericSearch( html5.Div ):
	def __init__(self, extension, view, modul, *args, **kwargs ):
		super( ExtendedNumericSearch, self ).__init__( *args, **kwargs )
		self.view = view
		self.extension = extension
		self.modul = modul
		self.opMode = extension["mode"]
		self.filterChangedEvent = EventDispatcher("filterChanged")
		assert self.opMode in ["equals","from", "to","range"]
		self.appendChild( html5.TextNode("NUMERIC SEARCH"))
		self.appendChild( html5.TextNode(extension["name"]))
		self.sinkEvent("onKeyDown")
		if self.opMode in ["equals","from", "to"]:
			self.input = html5.Input()
			self.input["type"] = "number"
			self.appendChild( self.input )
		elif self.opMode == "range":
			self.input1 = html5.Input()
			self.input1["type"] = "number"
			self.appendChild( self.input1 )
			self.appendChild( html5.TextNode("to") )
			self.input2 = html5.Input()
			self.input2["type"] = "number"
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
		return( isinstance( extension, dict) and "type" in extension.keys() and (extension["type"]=="numeric" or extension["type"].startswith("numeric.") ) )




def CheckForNumericBone(  modulName, boneName, skelStucture, *args, **kwargs ):
	return( skelStucture[boneName]["type"]=="numeric" )

#Register this Bone in the global queue
editBoneSelector.insert( 3, CheckForNumericBone, NumericEditBone)
viewDelegateSelector.insert( 3, CheckForNumericBone, NumericViewBoneDelegate)
extendedSearchWidgetSelector.insert( 1, ExtendedNumericSearch.canHandleExtension, ExtendedNumericSearch )
