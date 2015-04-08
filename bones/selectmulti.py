#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import html5, utils
from priorityqueue import editBoneSelector, viewDelegateSelector, extendedSearchWidgetSelector, extractorDelegateSelector
from event import EventDispatcher
from i18n import translate
from config import conf

class SelectMultiBoneExtractor( object ):
	def __init__(self, modulName, boneName, skelStructure, *args, **kwargs ):
		super(SelectMultiBoneExtractor, self ).__init__()
		self.skelStructure = skelStructure
		self.boneName = boneName
		self.modulName=modulName

	def render( self, data, field ):
		if field in data.keys():
			result = list()
			for fieldKey in data[field]:
				if not fieldKey in self.skelStructure[field]["values"].keys():
					result.append(fieldKey)
				else:
					value = self.skelStructure[field]["values"][fieldKey]
					if value:
						result.append(value)
			return ",".join(result)
		return conf[ "empty_value" ]

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
		return html5.Label("&nbsp; - &nbsp;")

class SelectMultiEditBone( html5.Div ):

	def __init__(self, modulName, boneName,readOnly, values, sortBy="keys", *args, **kwargs ):
		super( SelectMultiEditBone,  self ).__init__( *args, **kwargs )
		self.boneName = boneName
		self.readOnly = readOnly
		self.values=values
		tmpList = values.items()
		if sortBy=="keys":
			tmpList.sort( key=lambda x: x[0] ) #Sort by keys
		else:
			tmpList.sort( key=lambda x: x[1] ) #Values
		for key, value in tmpList:
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
		if "sortBy" in skelStructure[ boneName ].keys():
			sortBy = skelStructure[ boneName ][ "sortBy" ]
		else:
			sortBy = "keys"
		if "values" in skelStructure[ boneName ].keys():
			values =skelStructure[ boneName ]["values"]
		else:
			values = {}
		return( SelectMultiEditBone( modulName, boneName, readOnly, values, sortBy ) )

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

	def setExtendedErrorInformation(self, errorInfo ):
		pass

class ExtendedSelectMultiSearch( html5.Div ):
	def __init__(self, extension, view, modul, *args, **kwargs ):
		super( ExtendedSelectMultiSearch, self ).__init__( *args, **kwargs )
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
		return( isinstance( extension, dict) and "type" in extension.keys() and (extension["type"]=="selectmulti" or extension["type"].startswith("selectmulti.") ) )

def CheckForSelectMultiBone(  modulName, boneName, skelStucture, *args, **kwargs ):
	return skelStucture[boneName]["type"].startswith("selectmulti")

#Register this Bone in the global queue
editBoneSelector.insert( 3, CheckForSelectMultiBone, SelectMultiEditBone)
viewDelegateSelector.insert( 3, CheckForSelectMultiBone, SelectMultiViewBoneDelegate)
extendedSearchWidgetSelector.insert( 1, ExtendedSelectMultiSearch.canHandleExtension, ExtendedSelectMultiSearch )
extractorDelegateSelector.insert(3, CheckForSelectMultiBone, SelectMultiBoneExtractor)

#Class for AccessMultiSelectBone, a special bone to nicely present user access rights for all skeletons.
class AccessMultiSelectBone( html5.Div ):
	states = [ "view", "edit", "add", "delete" ]

	def __init__(self, moduleName, boneName, readOnly, values, *args, **kwargs ):
		super( AccessMultiSelectBone,  self ).__init__( *args, **kwargs )
		self.boneName = boneName
		self.modulName = moduleName
		self.readOnly = readOnly
		self.values = values
		self.modules = {}
		self.flags = {}
		self.sinkEvent( "onClick" )

		for value in values:
			module = self.parseskelaccess( value )
			if not module:
				self.flags[ value ] = None
			elif not module[ 0 ] in self.modules.keys():
				self.modules[ module[ 0 ] ] = {}

		# Render static / singleton flags first
		for flag in sorted( self.flags.keys() ):
			label = html5.Label()

			checkbox = html5.Input()
			checkbox["type"] = "checkbox"
			checkbox["name"] = flag
			label.appendChild( checkbox )

			self.flags[ flag ] = checkbox

			span = html5.Span()
			span.appendChild( html5.TextNode( flag ) )
			label.appendChild( span )

			self.appendChild( label )

		# Render module access flags then
		for module in sorted( self.modules.keys() ):
			label = html5.Label()

			span = html5.Span()
			span.appendChild( html5.TextNode( module ) )
			label.appendChild( span )

			ul = html5.Ul()
			for state in self.states:
				li = html5.Li()
				li[ "class" ] = [ "access-state", state ]

				# Some modules may not support all states
				if ( "%s-%s" % (module, state) ) not in self.values:
					li[ "class" ].append( "disabled" )

				ul.appendChild( li )

				self.modules[ module ][ state ] = li

			label.appendChild( ul )

			self.appendChild( label )

	def parseskelaccess( self, value ):
		for state in self.states:
			if value.endswith( state ):
				return ( value[ 0 :  -( len( state ) + 1 ) ], state )

		return False

	def onClick( self, event ):
		for skel, toggles in self.modules.items():
			for toggle in toggles.values():
				if utils.doesEventHitWidgetOrChildren( event, toggle ):
					if not "disabled" in toggle[ "class" ]:
						if "active" in toggle[ "class" ]:
							toggle[ "class" ].remove( "active" )

							# When disabling "view", disable all other flags also, because
							# they don't make no sense anymore then.
							if "view" in toggle[ "class" ]:
								for rm in [ "add", "delete", "edit" ]:
									self.modules[ skel ][ rm ][ "class" ].remove( "active" )

						else:
							toggle[ "class" ].append( "active" )

					return

	@staticmethod
	def fromSkelStructure( moduleName, boneName, skelStructure ):
		readOnly = "readonly" in skelStructure[ boneName ].keys() and skelStructure[ boneName ]["readonly"]

		if "values" in skelStructure[ boneName ].keys():
			values = skelStructure[ boneName ]["values"]
		else:
			values = {}

		return( AccessMultiSelectBone( moduleName, boneName, readOnly, values ) )

	def unserialize(self, data):
		if self.boneName in data.keys():
			values = data[ self.boneName ] if data[ self.boneName ] else []

			for name, elem in self.flags.items():
				if name in values:
					elem[ "checked" ] = True

			for skel in self.modules:
				for state in self.states:
					if "%s-%s" % ( skel, state ) in values:
						if not "active" in self.modules[ skel ][ state ][ "class" ]:
							self.modules[ skel ][ state ][ "class" ].append( "active" )


	def serializeForPost(self):
		ret = []

		for name, elem in self.flags.items():
			if elem[ "checked" ]:
				ret.append( name )

		for skel in self.modules:
			for state in self.states:
				if "active" in self.modules[ skel ][ state ][ "class" ]:
					ret.append( "%s-%s" % ( skel, state ) )

		return { self.boneName: ret }

	def serializeForDocument(self):
		return self.serialize()

def CheckForAccessMultiSelectBone( moduleName, boneName, skelStucture ):
	if skelStucture[boneName]["type"] == "selectmulti.access":
		return True

	return False

#Register this Bone in the global queue
editBoneSelector.insert( 4, CheckForAccessMultiSelectBone, AccessMultiSelectBone )
