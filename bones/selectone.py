#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import html5
from priorityqueue import editBoneSelector, viewDelegateSelector, extendedSearchWidgetSelector, extractorDelegateSelector
from event import EventDispatcher
from i18n import translate
from config import conf
from bones.base import BaseBoneExtractor

class SelectOneBoneExtractor(BaseBoneExtractor):
	def __init__(self, moduleName, boneName, skelStructure, *args, **kwargs ):
		super( SelectOneBoneExtractor, self ).__init__()
		self.skelStructure = skelStructure
		self.boneName = boneName
		self.moduleName=moduleName

	def render( self, data, field ):
		if field in data.keys():
			if data and field and field in self.skelStructure and data[field] and data[field] in self.skelStructure[field]["values"]:
				return self.skelStructure[field]["values"][data[field]]
		return conf[ "empty_value" ]


class SelectOneViewBoneDelegate( object ):
	def __init__(self, moduleName, boneName, skelStructure, *args, **kwargs ):
		super( SelectOneViewBoneDelegate, self ).__init__()
		self.skelStructure = skelStructure
		self.boneName = boneName
		self.moduleName = moduleName

	def render( self, data, field ):
		if field in data.keys():
			if data and field and field in self.skelStructure:
				options = {k: v for k, v in self.skelStructure[field]["values"]}

				aspan = html5.Span()
				aspan.appendChild(html5.TextNode(options.get(data[field], data[field])))
				aspan["Title"]=data[field]
				return aspan

		return html5.Label(conf["empty_value"])

class SelectOneEditBone( html5.Select ):

	def __init__(self, moduleName, boneName, readOnly, values, *args, **kwargs):
		super(SelectOneEditBone,  self).__init__(*args, **kwargs)
		self["name"] = self.boneName = boneName
		self.readOnly = readOnly

		# Compatibility mode
		if isinstance(values, dict):
			self.values = [(k, v) for k, v in values.items()]
		else:
			self.values = values

		# Perform valuesOrder list
		for (key, value) in self.values:
			opt = html5.Option()
			opt["value"] = key
			opt.element.innerHTML = value

			self.appendChild(opt)

		if self.readOnly:
			self["disabled"] = True

	@staticmethod
	def fromSkelStructure( moduleName, boneName, skelStructure ):
		return SelectOneEditBone(moduleName, boneName,
		                            skelStructure[boneName].get("readonly", False),
		                            skelStructure[boneName].get("values", {}))

	def unserialize(self, data):
		if self.boneName in data.keys():
			self.val = data[ self.boneName ] if data[ self.boneName ] else ""
			for aoption in self._children:
				if aoption["value"] == self.val:
					aoption["selected"]=True

	def serializeForPost(self):
		for opt in self.children():
			if opt["selected"]:
				return {self.boneName: opt["value"]}

		return {}

	def serializeForDocument(self):
		return self.serializeForPost()

class ExtendedSelectOneSearch( html5.Div ):
	def __init__(self, extension, view, modul, *args, **kwargs ):
		super( ExtendedSelectOneSearch, self ).__init__( *args, **kwargs )
		self.view = view
		self.extension = extension
		self.module = modul
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

def CheckForSelectOneBone(  moduleName, boneName, skelStucture, *args, **kwargs ):
	return( skelStucture[boneName]["type"]=="selectone" )

#Register this Bone in the global queue
editBoneSelector.insert( 3, CheckForSelectOneBone, SelectOneEditBone)
viewDelegateSelector.insert( 3, CheckForSelectOneBone, SelectOneViewBoneDelegate)
extendedSearchWidgetSelector.insert( 1, ExtendedSelectOneSearch.canHandleExtension, ExtendedSelectOneSearch )
extractorDelegateSelector.insert(3, CheckForSelectOneBone, SelectOneBoneExtractor)
