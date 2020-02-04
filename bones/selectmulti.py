# -*- coding: utf-8 -*-
from vi import html5

from vi.priorityqueue import editBoneSelector, viewDelegateSelector, extendedSearchWidgetSelector, extractorDelegateSelector
from vi.framework.event import EventDispatcher
from vi.i18n import translate
from vi.config import conf
from vi.bones.base import BaseBoneExtractor
from vi.framework.embedsvg import embedsvg

class SelectMultiBoneExtractor(BaseBoneExtractor):

	def render(self, data, field):
		if field in data.keys():
			options = {k: v for k, v in self.skelStructure[field]["values"]}
			result = list()

			for fieldKey in data[field]:
				if not fieldKey in options.keys():
					result.append(fieldKey)
				else:
					value = options.get(fieldKey)
					if value:
						result.append(value)

			return ",".join(result)

		return conf["emptyValue"]

class SelectMultiViewBoneDelegate( object ):
	def __init__(self, moduleName, boneName, skelStructure, *args, **kwargs ):
		super( SelectMultiViewBoneDelegate, self ).__init__()
		self.skelStructure = skelStructure
		self.boneName = boneName
		self.moduleName = moduleName

	def render( self, data, field ):

		if field in data.keys():
			delegato = html5.Ul()
			options = {k: v for k, v in self.skelStructure[field]["values"]}

			for i, fieldKey in enumerate(data[field]):
				if conf["maxMultiBoneEntries"] and i + 1 > conf["maxMultiBoneEntries"]:
					ali = html5.Li()
					ali.appendChild(
						html5.TextNode(translate("and {count} more",
						                            count=len(data[field]) - conf["maxMultiBoneEntries"])))
					ali.addClass("selectmulti_more_li")

					delegato.appendChild(ali)
					break

				ali = html5.Li()
				ali.appendChild(html5.TextNode(options.get(fieldKey, fieldKey)))
				ali["Title"] = fieldKey

				delegato.appendChild(ali)

			return delegato
		else:
			delegato = html5.Div(conf["emptyValue"])

		delegato.addClass("vi-delegato", "vi-delegato--select", "vi-delegato--selectmulti")
		return delegato

class SelectMultiEditBone(html5.Div):

	def __init__(self, moduleName, boneName, readOnly, values, *args, **kwargs):
		super(SelectMultiEditBone,  self ).__init__(*args, **kwargs)
		self.boneName = boneName
		self.readOnly = readOnly
		self.addClass("vi-bone-container option-group")

		# Compatibility mode
		if isinstance(values, dict):
			self.values = [(k, v) for k, v in values.items()]
		else:
			self.values = values

		# Perform valuesOrder list
		for key, value in self.values:
			alabel = html5.Label()
			alabel.addClass("check")
			acheckbox = html5.Input()
			acheckbox["type"] = "checkbox"
			acheckbox["name"] = key
			acheckbox.addClass("check-input")
			alabel.appendChild(acheckbox)

			aspan = html5.Span()
			aspan.addClass("check-label")
			aspan.element.innerHTML = value
			alabel.appendChild(aspan)

			self.appendChild(alabel)

		if self.readOnly:
			self["disabled"] = True

	@staticmethod
	def fromSkelStructure(moduleName, boneName, skelStructure, *args, **kwargs):
		return SelectMultiEditBone(moduleName, boneName,
		                            skelStructure[boneName].get("readonly", False),
		                            skelStructure[boneName].get("values", {}))

	def unserialize(self, data):
		if self.boneName in data.keys():
			self.val = data[ self.boneName ] if data[ self.boneName ] else []
			for alabel in self._children:
				if alabel._children[0]["name"] in self.val:
					alabel._children[0]["checked"]=True

	def serializeForPost(self):
		value = []

		for alabel in self._children:
			if alabel._children[0]["checked"]:
				value.append(alabel._children[0]["name"])

		return {self.boneName: value}

	def serializeForDocument(self):
		return self.serializeForPost()

	def setExtendedErrorInformation(self, errorInfo ):
		pass

class ExtendedSelectMultiSearch( html5.Div ):
	def __init__(self, extension, view, module, *args, **kwargs ):
		super( ExtendedSelectMultiSearch, self ).__init__( *args, **kwargs )
		self.view = view
		self.extension = extension
		self.module = module
		self.filterChangedEvent = EventDispatcher("filterChanged")
		self.appendChild( html5.TextNode(extension["name"]))
		self.selectionCb = html5.Select()
		self.addClass("select")
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
	def canHandleExtension( extension, view, module ):
		return (isinstance(extension, dict)
		        and "type" in extension.keys()
		        and (
			            ((extension["type"] == "select" or extension["type"].startswith("select."))
		                    and extension.get("multiple", False))
		            or (extension["type"] == "selectmulti" or extension["type"].startswith("selectmulti."))))

def CheckForSelectMultiBone(moduleName, boneName, skelStructure, *args, **kwargs):
	return (((skelStructure[boneName]["type"] == "select" or skelStructure[boneName]["type"].startswith("select."))
	        and skelStructure[boneName].get("multiple", False))
	        or ((skelStructure[boneName]["type"] == "selectmulti" or skelStructure[boneName]["type"].startswith("selectmulti."))))

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
		self.moduleName = moduleName
		self.readOnly = readOnly

		self.values = {k: v for k, v in values}
		self.addClass("vi-bone-container option-group")

		self.modules = {}
		self.modulesbox = {}
		self.flags = {}

		self.sinkEvent( "onClick" )
		self.sinkEvent( "onKeyPress" )

		for value in self.values:
			module = self.parseskelaccess( value )

			if not module:
				self.flags[ value ] = None
			elif not module[ 0 ] in self.modules.keys():
				self.modules[ module[ 0 ] ] = {}

		self.searchfield = html5.Input()
		self.searchfield["style"]["width"] = "400px"
		self.searchfield["placeholder"] = translate( "Zugriffsrecht finden..." )
		self.appendChild(self.searchfield)


		# Render static / singleton flags first
		for flag in sorted( self.flags.keys() ):
			label = html5.Label()
			label.addClass("check")
			label["data"]["name"] = flag.lower()

			checkbox = html5.Input()
			checkbox["type"] = "checkbox"
			checkbox["name"] = flag
			checkbox.addClass("check-input")
			label.appendChild( checkbox )

			self.flags[ flag ] = checkbox

			span = html5.Span()
			span.addClass("check-label")
			span.appendChild( html5.TextNode( flag ) )
			label.appendChild( span )

			self.appendChild( label )

		# Render module access flags then
		for module in sorted( self.modules.keys() ):
			label = html5.Label()
			label.addClass("check")
			self.appendChild( label )

			checkbox = html5.Input()
			checkbox["type"] = "checkbox"
			checkbox["name"] = module
			checkbox.addClass("check-input")
			self.modulesbox[ module ] = checkbox
			label.appendChild( checkbox )

			span = html5.Span()
			span.addClass("check-label")

			title = conf["modules"][module]["name"]
			title = title if title else module
			label._getData()["name"] = title
			label.element.setAttribute( str("data-name"), title.lower() )
			span.appendChild( html5.TextNode(title) )

			label.appendChild( span )

			ul = html5.Ul()
			ul.addClass("input-group")
			for state in self.states:
				li = html5.Li()
				li[ "class" ] = [ "btn btn--access-state", state ]
				svg = embedsvg.get("icons-%s" % state)
				if state == "view":
					svg = embedsvg.get("icons-preview")
				if svg:
					li.element.innerHTML = svg + li.element.innerHTML
				li.appendChild( html5.TextNode( translate(state) ) )

				# Some modules may not support all states
				if ( "%s-%s" % (module, state) ) not in self.values:
					li[ "class" ].append( "is-disabled" )

				ul.appendChild( li )

				self.modules[ module ][ state ] = li
			label.appendChild( ul )


	def parseskelaccess( self, value ):
		for state in self.states:
			if value.endswith( "-" + state ):
				return ( value[ 0 :  -( len( state ) + 1 ) ], state )

		return False

	def onKeyPress(self, event):
		if html5.utils.doesEventHitWidgetOrChildren(event,self.searchfield) and event.keyCode == 13:
			value = self.searchfield["value"]
			for el in self._children:

				if isinstance(el,html5.Label):
					el["class"].remove("is-hidden")
					if not value:
						continue

					if value.lower() not in str(el.element.getAttribute("data-name")):
						el["class"].append("is-hidden")


	def onClick( self, event ):
		for module, toggles in self.modules.items():
			for toggle in toggles.values():
				if html5.utils.doesEventHitWidgetOrChildren(event, toggle):
					if not "is-disabled" in toggle[ "class" ]:
						if "is-active" in toggle[ "class" ]:
							toggle[ "class" ].remove( "is-active" )

							# When disabling "view", disable all other flags also, because
							# they don't make no sense anymore then.
							if "view" in toggle[ "class" ]:
								for rm in [ "add", "delete", "edit" ]:
									self.modules[ module ][ rm ][ "class" ].remove( "is-active" )

						else:
							toggle[ "class" ].append( "is-active" )

					self.checkmodulesbox( module )

					event.preventDefault()
					return

			if html5.utils.doesEventHitWidgetOrChildren(event, self.modulesbox[module]):
				self.modulesbox[ module ].parent().removeClass("partly")

				for toggle in toggles.values():
					if not "disabled" in toggle[ "class" ]:
						if self.modulesbox[ module ][ "checked" ]:
							if not "is-active" in toggle[ "class" ]:
								toggle[ "class" ].append( "is-active" )
						else:
							toggle[ "class" ].remove( "is-active" )

				return

	def checkmodulesbox(self, module):
		on = 0
		all = 0

		for item in self.modules[ module ].values():
			if not "disabled" in item[ "class" ]:
				all += 1

			if "is-active" in item[ "class" ]:
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
	def fromSkelStructure(moduleName, boneName, skelStructure, *args, **kwargs):
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
						if not "is-active" in self.modules[ module ][ state ][ "class" ]:
							self.modules[ module ][ state ][ "class" ].append( "is-active" )

				self.checkmodulesbox( module )


	def serializeForPost(self):
		ret = []

		for name, elem in self.flags.items():
			if elem[ "checked" ]:
				ret.append( name )

		for module in self.modules:
			for state in self.states:
				if "is-active" in self.modules[ module ][ state ][ "class" ]:
					ret.append( "%s-%s" % ( module, state ) )

		return {self.boneName: ret}

	def serializeForDocument(self):
		return self.serializeForPost()

def CheckForAccessMultiSelectBone(moduleName, boneName, skelStructure, *args, **kwargs):
	print(moduleName, boneName, skelStructure[boneName]["type"], skelStructure[boneName]["type"] in ["select.access", "selectmulti.access"])
	return skelStructure[boneName]["type"] in ["select.access", "selectmulti.access"]

#Register this Bone in the global queue
editBoneSelector.insert( 4, CheckForAccessMultiSelectBone, AccessMultiSelectBone )
