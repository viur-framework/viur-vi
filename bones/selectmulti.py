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
		self.modulName = modulName

	def render( self, data, field ):
		if field in data.keys():
			result = html5.Ul()
			options = {k: v for k, v in self.skelStructure[field]["values"]}

			for i, fieldKey in enumerate(data[field]):
				if conf["maxMultiBoneEntries"] and i == conf["maxMultiBoneEntries"]:
					ali = html5.Li()
					ali.appendChild(
						html5.TextNode(translate("and {count} more",
						                            count=len(data[field]) - conf["maxMultiBoneEntries"] - 1)))
					ali["class"].append("selectmulti_more_li")

					result.appendChild(ali)
					break

				ali = html5.Li()
				ali.appendChild(html5.TextNode(options.get(fieldKey, fieldKey)))
				ali["Title"] = fieldKey

				result.appendChild(ali)

			return result

		return html5.Label(conf["empty_value"])

class SelectMultiEditBone(html5.Div):

	def __init__(self, moduleName, boneName, readOnly, values, *args, **kwargs):
		super(SelectMultiEditBone,  self ).__init__(*args, **kwargs)
		self.boneName = boneName
		self.readOnly = readOnly

		# Compatibility mode
		if isinstance(values, dict):
			self.values = [(k, v) for k, v in values.items()]
		else:
			self.values = values

		# Perform valuesOrder list
		for key, value in self.values:
			alabel = html5.Label()
			acheckbox = html5.Input()
			acheckbox["type"] = "checkbox"
			acheckbox["name"] = key
			alabel.appendChild(acheckbox)

			aspan = html5.Span()
			aspan.element.innerHTML = value
			alabel.appendChild(aspan)

			self.appendChild(alabel)

		if self.readOnly:
			self["disabled"] = True

	@staticmethod
	def fromSkelStructure( modulName, boneName, skelStructure ):
		return SelectMultiEditBone(modulName, boneName,
		                            skelStructure[boneName].get("readonly", False),
		                            skelStructure[boneName].get("values", {}))

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
		print(values)
		self.values = {k: v for k, v in values}

		self.modules = {}
		self.modulesbox = {}
		self.flags = {}

		self.sinkEvent( "onClick" )

		for value in self.values:
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

			checkbox = html5.Input()
			checkbox["type"] = "checkbox"
			checkbox["name"] = module
			self.modulesbox[ module ] = checkbox

			li = html5.Li()
			li.appendChild( checkbox )
			ul.appendChild( li )

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
		for module, toggles in self.modules.items():
			for toggle in toggles.values():
				if html5.utils.doesEventHitWidgetOrChildren(event, toggle):
					if not "disabled" in toggle[ "class" ]:
						if "active" in toggle[ "class" ]:
							toggle[ "class" ].remove( "active" )

							# When disabling "view", disable all other flags also, because
							# they don't make no sense anymore then.
							if "view" in toggle[ "class" ]:
								for rm in [ "add", "delete", "edit" ]:
									self.modules[ module ][ rm ][ "class" ].remove( "active" )

						else:
							toggle[ "class" ].append( "active" )

					self.checkmodulesbox( module )

					event.preventDefault()
					return

			if html5.utils.doesEventHitWidgetOrChildren(event, self.modulesbox[module]):
				self.modulesbox[ module ].parent()["class"].remove("partly")

				for toggle in toggles.values():
					if not "disabled" in toggle[ "class" ]:
						if self.modulesbox[ module ][ "checked" ]:
							if not "active" in toggle[ "class" ]:
								toggle[ "class" ].append( "active" )
						else:
							toggle[ "class" ].remove( "active" )

				return

	def checkmodulesbox(self, module):
		on = 0
		all = 0

		for item in self.modules[ module ].values():
			if not "disabled" in item[ "class" ]:
				all += 1

			if "active" in item[ "class" ]:
				on += 1

		if on == 0 or on == all:
			self.modulesbox[ module ].parent()[ "class" ].remove( "partly" )
			self.modulesbox[ module ][ "indeterminate" ] = False
			self.modulesbox[ module ][ "checked" ] = ( on == all )
		else:
			self.modulesbox[ module ][ "checked" ] = False
			self.modulesbox[ module ][ "indeterminate" ] = True

			if not "partly" in self.modulesbox[ module ].parent()[ "class" ]:
				self.modulesbox[ module ].parent()[ "class" ].append( "partly" )

	@staticmethod
	def fromSkelStructure( moduleName, boneName, skelStructure ):
		return AccessMultiSelectBone(moduleName, boneName, skelStructure[ boneName ].get("readonly", False),
		                                                    skelStructure[boneName].get("values", []))

	def unserialize(self, data):
		if self.boneName in data.keys():
			values = data[ self.boneName ] if data[ self.boneName ] else []

			for name, elem in self.flags.items():
				if name in values:
					elem[ "checked" ] = True

			for module in self.modules:
				for state in self.states:
					if "%s-%s" % ( module, state ) in values:
						if not "active" in self.modules[ module ][ state ][ "class" ]:
							self.modules[ module ][ state ][ "class" ].append( "active" )

				self.checkmodulesbox( module )


	def serializeForPost(self):
		ret = []

		for name, elem in self.flags.items():
			if elem[ "checked" ]:
				ret.append( name )

		for module in self.modules:
			for state in self.states:
				if "active" in self.modules[ module ][ state ][ "class" ]:
					ret.append( "%s-%s" % ( module, state ) )

		return { self.boneName: ret }

	def serializeForDocument(self):
		return self.serialize()

def CheckForAccessMultiSelectBone( moduleName, boneName, skelStucture ):
	if skelStucture[boneName]["type"] == "selectmulti.access":
		return True

	return False

#Register this Bone in the global queue
editBoneSelector.insert( 4, CheckForAccessMultiSelectBone, AccessMultiSelectBone )
