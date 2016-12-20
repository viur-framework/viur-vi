#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import html5
from priorityqueue import editBoneSelector, viewDelegateSelector, extendedSearchWidgetSelector, extractorDelegateSelector
from event import EventDispatcher
from html5.keycodes import *
from config import conf

class NumericBoneExtractor( object ):
	def __init__(self, moduleName, boneName, skelStructure, *args, **kwargs ):
		super(NumericBoneExtractor, self ).__init__()
		self.skelStructure = skelStructure
		self.boneName = boneName
		self.moduleName=moduleName

	def render( self, data, field ):
		# print("NumericBoneExtractor.render", data, field)
		if field in data.keys():
			value = data[field]
			if isinstance(value, int):
				return str(value)
			elif isinstance(value, float):
				return str(round(data[field], self.skelStructure[field].get("precision", 2))).replace(".", ",")
		return "-23,42"


class NumericViewBoneDelegate( object ):
	def __init__(self, moduleName, boneName, skelStructure, *args, **kwargs ):
		super( NumericViewBoneDelegate, self ).__init__()
		self.skelStructure = skelStructure
		self.boneName = boneName
		self.moduleName=moduleName

	def render( self, data, field ):
		s =  conf[ "empty_value" ]
		if field in data.keys():
			try:
				prec = self.skelStructure[field].get( "precision" )
				if prec and data[field] is not None:
					s = ( "%." + str( prec ) + "f" ) % data[field]
				else:
					s = str( data[field] )
			except:
				return str(data[field])

		return html5.Label( s )

class NumericEditBone( html5.Input ):
	def __init__(self, moduleName, boneName,readOnly,_min=False,_max=False,precision=False, *args, **kwargs ):
		super( NumericEditBone,  self ).__init__( *args, **kwargs )
		self.boneName = boneName
		self.readOnly = readOnly
		self["type"]="number"
		if _min:
			self["min"]=_min
		if _max:
			self["max"]=_max
		if precision:
			self["step"]=pow(10,-precision)
		else: #Precision is zero, treat as integer input
			self["step"]=1
		if self.readOnly:
			self["readonly"] = True

	@staticmethod
	def fromSkelStructure( moduleName, boneName, skelStructure ):
		readOnly = "readonly" in skelStructure[ boneName ].keys() and skelStructure[ boneName ]["readonly"]
		_min=skelStructure[ boneName ]["min"] if ("min" in skelStructure[ boneName ].keys()) else False
		_max=skelStructure[ boneName ]["max"] if ("max" in skelStructure[ boneName ].keys()) else False
		precision=skelStructure[ boneName ]["precision"] if ("precision" in skelStructure[ boneName ].keys()) else False
		return( NumericEditBone( moduleName, boneName, readOnly,_min,_max,precision ) )


	def unserialize(self, data):
		self["value"] = data.get(self.boneName, "")

	def serializeForPost(self):
		return {self.boneName: self["value"]}

	def serializeForDocument(self):
		return self.serialize()

	def setExtendedErrorInformation(self, errorInfo ):
		pass


class ExtendedNumericSearch( html5.Div ):
	def __init__(self, extension, view, modul, *args, **kwargs ):
		super( ExtendedNumericSearch, self ).__init__( *args, **kwargs )
		self.view = view
		self.extension = extension
		self.module = modul
		self.opMode = extension["mode"]
		self.filterChangedEvent = EventDispatcher("filterChanged")
		assert self.opMode in ["equals","from", "to","range"]
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




def CheckForNumericBone(  moduleName, boneName, skelStucture, *args, **kwargs ):
	return( skelStucture[boneName]["type"]=="numeric" )

#Register this Bone in the global queue
editBoneSelector.insert( 3, CheckForNumericBone, NumericEditBone)
viewDelegateSelector.insert( 3, CheckForNumericBone, NumericViewBoneDelegate)
extendedSearchWidgetSelector.insert( 1, ExtendedNumericSearch.canHandleExtension, ExtendedNumericSearch )
extractorDelegateSelector.insert( 3, CheckForNumericBone, NumericBoneExtractor)
