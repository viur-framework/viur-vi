#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import html5
from priorityqueue import editBoneSelector, viewDelegateSelector
from datetime import datetime

class DateViewBoneDelegate( object ):
	def __init__(self, modulName, boneName, skelStructure, *args, **kwargs ):
		super( DateViewBoneDelegate, self ).__init__()
		self.skelStructure = skelStructure
		self.boneName = boneName
		self.modulName=modulName

	def render( self, data, field ):
		if field in data.keys():
			return( html5.Label(str( data[field])))
		return( html5.Label("..") )

class DateEditBone( html5.Input ):
	def __init__(self, modulName, boneName,readOnly,date=True, time=True, *args, **kwargs ):
		super( DateEditBone,  self ).__init__( *args, **kwargs )
		self.boneName = boneName
		self.readOnly = readOnly
		if not date and time:
			self["type"]="time"
		elif not time and date:
			self["type"]="date"
		else:
			self["type"]="datetime-local"

	@staticmethod
	def fromSkelStructure( modulName, boneName, skelStructure ):
		readOnly = "readonly" in skelStructure[ boneName ].keys() and skelStructure[ boneName ]["readonly"]
		date = skelStructure[ boneName ]["date"] if "date" in skelStructure[ boneName ].keys() else True
		time = skelStructure[ boneName ]["time"] if "time" in skelStructure[ boneName ].keys() else True
		return( DateEditBone( modulName, boneName, readOnly ) )

	def unserialize(self, data):
		if self.boneName in data.keys():
			dateobj=datetime.strptime(data[ self.boneName ], "%d.%m.%Y %H:%M:%S")
			self["value"]=dateobj.strftime( "%Y-%m-%dT%H:%M" )

	def serializeForPost(self):
		dateobj=datetime.strptime(self["value"], "%Y-%m-%dT%H:%M")
		return( { self.boneName: dateobj.strftime("%d.%m.%Y %H:%M:00") } )

	def serializeForDocument(self):
		return( self.serialize( ) )

def CheckForDateBone(  modulName, boneName, skelStucture ):
	return( skelStucture[boneName]["type"]=="date" )

#Register this Bone in the global queue
editBoneSelector.insert( 3, CheckForDateBone, DateEditBone)
viewDelegateSelector.insert( 3, CheckForDateBone, DateViewBoneDelegate)
