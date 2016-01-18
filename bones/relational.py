#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os.path
import re
import html5
from priorityqueue import editBoneSelector, viewDelegateSelector, extendedSearchWidgetSelector, extractorDelegateSelector
from event import EventDispatcher
from utils import formatString
from widgets.list import ListWidget
from config import conf
from i18n import translate
from network import NetworkService
from widgets.edit import EditWidget
from pane import Pane

class RelationalBoneExtractor(object):
	def __init__(self, modul, boneName, structure):
		super(RelationalBoneExtractor, self).__init__()
		self.format = "$(name)"
		if "format" in structure[boneName].keys():
			self.format = structure[boneName]["format"]
		try:
			self.format = re.match("\$\((.*?)\)", self.format).group(1)
		except:
			pass

		try:
			self.format, blah = os.path.splitext(self.format)
		except ValueError:
			pass

		self.modul = modul
		self.structure = structure
		self.boneName = boneName

	def render(self, data, field ):
		def localizedRender(val, format):
			if "currentlanguage" in conf:
				i18n_val = "%s.%s" % (self.format, conf["currentlanguage"])

				if i18n_val in val:
					val = html5.utils.unescape(val[i18n_val])
				elif format in val:
					val = html5.utils.unescape(str(val[format]))
				elif val:
					val = val["key"]

			else:
				val = val["key"]

			return val

		assert field == self.boneName, "render() was called with field %s, expected %s" % (field,self.boneName)
		if field in data.keys():
			val = data[field]
		else:
			val = ""

		if isinstance(val, list):
			result = list()
			for x in val:
				result.append(localizedRender(x, self.format))

			return ", ".join(result)

		elif isinstance(val, dict):
			val = localizedRender(val, self.format)

		else:
			print("warning type:", val, type(val))

		return html5.utils.unescape(val)


class RelationalViewBoneDelegate( object ):
	cantSort = True
	def __init__(self, modul, boneName, structure):
		super(RelationalViewBoneDelegate, self).__init__()
		self.format = "$(name)"
		if "format" in structure[boneName].keys():
			self.format = structure[boneName]["format"]
		self.modul = modul
		self.structure = structure
		self.boneName = boneName

	def render(self, data, field ):
		assert field == self.boneName, "render() was called with field %s, expected %s" % (field,self.boneName)

		if field in data.keys():
			val = data[field]
		else:
			val = ""

		if isinstance(val,list):
			if len(val)<5:
				res = ", ".join( [ (formatString(self.format, self.structure, x, unescape= True) or x["key"]) for x in val] )
			else:
				res = ", ".join( [ (formatString(self.format, self.structure, x, unescape= True) or x["key"]) for x in val[:4]] )
				res += " "+translate("and {count} more",count=len(val)-4)
			#val = ", ".join( [(x["name"] if "name" in x.keys() else x["key"]) for x in val])
		elif isinstance(val, dict):
			res = formatString(self.format,self.structure, val, unescape= True) or val["key"]
			#val = val["name"] if "name" in val.keys() else val["key"]
		return( html5.Label( res ) )
		#return( formatString( self.format, self.structure, value ) ) FIXME!


class RelationalSingleSelectionBone( html5.Div ):
	"""
		Provides the widget for a relationalBone with multiple=False
	"""

	def __init__(self, srcModul, boneName, readOnly, destModul, format="$(name)", required=False, *args, **kwargs ):
		"""
			@param srcModul: Name of the modul from which is referenced
			@type srcModul: string
			@param boneName: Name of the bone thats referencing
			@type boneName: string
			@param readOnly: Prevents modifying its value if set to True
			@type readOnly: bool
			@param destModul: Name of the modul which gets referenced
			@type destModul: string
			@param format: Specifies how entries should be displayed.
			@type format: string
		"""
		super( RelationalSingleSelectionBone,  self ).__init__( *args, **kwargs )
		self.srcModul = srcModul
		self.boneName = boneName
		self.readOnly = readOnly
		self.destModul = destModul
		self.format = format
		self.selection = None
		self.selectionTxt = html5.Input()
		self.selectionTxt["type"] = "text"
		self.selectionTxt["readonly"] = True
		self.appendChild( self.selectionTxt )
		#DOM.setElemAttribute( self.selectionTxt, "type", "text")
		#DOM.appendChild(self.getElement(), self.selectionTxt )

		# Selection button
		if ( "root" in conf[ "currentUser" ][ "access" ]
		     or destModul + "-view" in conf[ "currentUser" ][ "access" ] ):
			self.selectBtn = html5.ext.Button(translate("Select"), self.onShowSelector)
			self.selectBtn["class"].append("icon")
			self.selectBtn["class"].append("select")
			self.appendChild( self.selectBtn )
		else:
			self.selectBtn = None

		# Edit button
		if ( "root" in conf[ "currentUser" ][ "access" ]
		     or destModul + "-edit" in conf[ "currentUser" ][ "access" ] ):
			self.editBtn = html5.ext.Button(translate("Edit"), self.onEdit )
			self.editBtn["class"].append("icon")
			self.editBtn["class"].append("edit")
			self.appendChild( self.editBtn )
		else:
			self.editBtn = None

		# Remove button
		if ( not required and not readOnly
		     and ("root" in conf[ "currentUser" ][ "access" ]
		            or destModul + "-view" in conf[ "currentUser" ][ "access" ])):
			# Yes, we check for "view" on the remove button, because removal of relations
			# is only useful when viewing the destination module is still allowed.

			self.remBtn = html5.ext.Button(translate("Remove"), self.onRemove )
			self.remBtn["class"].append("icon")
			self.remBtn["class"].append("cancel")
			self.appendChild( self.remBtn )
		else:
			self.remBtn = None

		if self.readOnly:
			self["disabled"] = True
		#DOM.appendChild( self.getElement(), self.selectBtn.getElement())
		#self.selectBtn.onAttach()

	def _setDisabled(self, disable):
		"""
			Reset the is_active flag (if any)
		"""
		super(RelationalSingleSelectionBone, self)._setDisabled( disable )
		if not disable and not self._disabledState and "is_active" in self.parent()["class"]:
			self.parent()["class"].remove("is_active")

	@classmethod
	def fromSkelStructure( cls, modulName, boneName, skelStructure ):
		"""
			Constructs a new RelationalSingleSelectionBone from the parameters given in skelStructure.
			@param modulName: Name of the modul which send us the skelStructure
			@type modulName: string
			@param boneName: Name of the bone which we shall handle
			@type boneName: string
			@param skelStructure: The parsed skeleton structure send by the server
			@type skelStructure: dict
		"""
		readOnly = "readonly" in skelStructure[ boneName ].keys() and skelStructure[ boneName ]["readonly"]
		multiple = skelStructure[boneName]["multiple"]
		if "required" in skelStructure[boneName].keys() and skelStructure[boneName]["required"]:
			required=True
		else:
			required=False
		if "modul" in skelStructure[ boneName ].keys():
			destModul = skelStructure[ boneName ][ "modul" ]
		else:
			destModul = skelStructure[ boneName ]["type"].split(".")[1]
		format= "$(name)"
		if "format" in skelStructure[ boneName ].keys():
			format = skelStructure[ boneName ]["format"]
		return( cls( modulName, boneName, readOnly, destModul=destModul, format=format, required=required ) )

	def onEdit(self, *args, **kwargs):
		"""
			Edit the reference.
		"""
		if not self.selection:
			return

		pane = Pane( translate("Edit"), closeable=True, iconClasses=[ "modul_%s" % self.destModul,
		                                                                    "apptype_list", "action_edit" ] )
		conf["mainWindow"].stackPane( pane, focus=True )
		edwg = EditWidget( self.destModul, EditWidget.appList, key=self.selection[ "key" ] )
		pane.addWidget( edwg )

	def onRemove(self, *args, **kwargs):
		self.setSelection( None )

	def unserialize(self, data):
		"""
			Parses the values received from the server and update our value accordingly.
			@param data: The data dictionary received.
			@type data: dict
		"""
		if self.boneName in data.keys():
			val = data[ self.boneName ]
			if isinstance( val, list ):
				if len(val)>0:
					val = val[0]
				else:
					val = None
			if isinstance( val, dict ):
				self.setSelection( val )
			else:
				self.setSelection( None )
			#self.setText( data[ self.boneName ] if data[ self.boneName ] else "" )
			#self.lineEdit.setText( str( data[ self.boneName ] ) if data[ self.boneName ] else "" )

	def serializeForPost(self):
		"""
			Serializes our value into something that can be transferred to the server using POST.
			@returns: dict
		"""
		return( { self.boneName: self.selection["key"] if self.selection is not None else "" } )

	def serializeForDocument(self):
		return( self.serialize( ) )

	def onShowSelector(self, *args, **kwargs):
		"""
			Opens a ListWidget so that the user can select new values
		"""
		currentSelector = ListWidget( self.destModul, isSelector=True )
		currentSelector.selectionActivatedEvent.register( self )
		conf["mainWindow"].stackWidget( currentSelector )
		self.parent()["class"].append("is_active")

	def onSelectionActivated(self, table, selection ):
		"""
			Merges the selection made in the ListWidget into our value(s)
		"""
		if selection:
			self.setSelection( selection[0] )
		else:
			self.setSelection( None )

	def setSelection(self, selection):
		"""
			Set our current value to 'selection'
			@param selection: The new entry that this bone should reference
			@type selection: dict
		"""
		self.selection = selection
		if selection:
			NetworkService.request( self.destModul, "view/"+selection["key"],
			                            successHandler=self.onSelectionDataAviable, cacheable=True)
			self.selectionTxt["value"] = translate("Loading...")
		else:
			self.selectionTxt["value"] = ""

		self.updateButtons()

	def updateButtons(self):
		"""
		Updates the display style of the Edit and Remove buttons.
		"""
		if self.selection:
			if self.editBtn:
				self.editBtn[ "disabled" ] = False
			if self.remBtn:
				self.remBtn[ "disabled"] = False
		else:
			if self.editBtn:
				self.editBtn[ "disabled" ] = True
			if self.remBtn:
				self.remBtn[ "disabled"] = True

	def onAttach(self):
		super( RelationalSingleSelectionBone,  self ).onAttach()
		NetworkService.registerChangeListener( self )

	def onDetach(self):
		NetworkService.removeChangeListener( self )
		super( RelationalSingleSelectionBone,  self ).onDetach()

	def onDataChanged(self, modul):
		if modul == self.destModul:
			self.setSelection(self.selection)

	def onSelectionDataAviable(self, req):
		"""
			We just received the full information for this entry from the server and can start displaying it
		"""
		data = NetworkService.decode( req )
		assert self.selection["key"]==data["values"]["key"]
		self.selectionTxt["value"] = formatString( self.format ,data["structure"],data["values"] )

class RelationalMultiSelectionBoneEntry( html5.Div ):
	"""
		Wrapper-class that holds one referenced entry in a RelationalMultiSelectionBone.
		Provides the UI to display its data and a button to remove it from the bone.
	"""

	def __init__(self, parent, modul, data, format="$(name)", *args, **kwargs ):
		"""
			@param parent: Reference to the RelationalMultiSelectionBone we belong to
			@type parent: RelationalMultiSelectionBone
			@param modul: Name of the modul which references
			@type modul: String
			@param data: Values of the entry we shall display
			@type data: dict
		"""
		super( RelationalMultiSelectionBoneEntry, self ).__init__( *args, **kwargs )
		self.parent = parent
		self.modul = modul
		self.data = data
		self.format = format
		self.selectionTxt = html5.Span(  )
		self.selectionTxt.appendChild( html5.TextNode(translate("Loading...")) )
		self.selectionTxt["class"].append("entrydescription")
		self.appendChild( self.selectionTxt )

		#Edit button
		if ( "root" in conf[ "currentUser" ][ "access" ]
		     or modul + "-edit" in conf[ "currentUser" ][ "access" ] ):
			editBtn = html5.ext.Button("Edit", self.onEdit )
			editBtn["class"].append("icon")
			editBtn["class"].append("edit")
			self.appendChild( editBtn )

		#Remove button
		if (not parent.readOnly
			and ("root" in conf[ "currentUser" ][ "access" ]
			        or modul + "-view" in conf[ "currentUser" ][ "access" ])):
			# Check on "view" is also correct here - relational
			# can be removed if entries can be selected!
			remBtn = html5.ext.Button("Remove", self.onRemove )
			remBtn["class"].append("icon")
			remBtn["class"].append("cancel")
			self.appendChild( remBtn )

		self.fetchEntry( self.data["key"] )

	def fetchEntry(self, id):
		NetworkService.request(self.modul,"view/"+id, successHandler=self.onSelectionDataAviable, cacheable=True)

	def onEdit(self, *args, **kwargs):
		"""
			Edit the reference entry.
		"""
		pane = Pane( translate("Edit"), closeable=True, iconClasses=[ "modul_%s" % self.parent.destModul,
		                                                                    "apptype_list", "action_edit" ] )
		conf["mainWindow"].stackPane( pane, focus=True )
		edwg = EditWidget( self.parent.destModul, EditWidget.appList, key=self.data[ "key" ] )
		pane.addWidget( edwg )

	def onRemove(self, *args, **kwargs):
		self.parent.removeEntry( self )

	def onSelectionDataAviable(self, req):
		"""
			We just received the full information for this entry from the server and can start displaying it
		"""
		data = NetworkService.decode( req )
		assert self.data["key"]==data["values"]["key"]
		for c in self.selectionTxt._children[:]:
			self.selectionTxt.removeChild( c )
		self.selectionTxt.appendChild( html5.TextNode( formatString( self.format ,data["structure"],data["values"] ) ) )


class RelationalMultiSelectionBone( html5.Div ):
	"""
		Provides the widget for a relationalBone with multiple=True
	"""

	def __init__(self, srcModul, boneName, readOnly, destModul, format="$(name)", *args, **kwargs ):
		"""
			@param srcModul: Name of the modul from which is referenced
			@type srcModul: string
			@param boneName: Name of the bone thats referencing
			@type boneName: string
			@param readOnly: Prevents modifying its value if set to True
			@type readOnly: bool
			@param destModul: Name of the modul which gets referenced
			@type destModul: string
			@param format: Specifies how entries should be displayed.
			@type format: string
		"""
		super( RelationalMultiSelectionBone,  self ).__init__( *args, **kwargs )
		#self["class"].append("relational")
		#self["class"].append("multiple")
		self.srcModul = srcModul
		self.boneName = boneName
		self.readOnly = readOnly
		self.destModul = destModul
		self.format = format
		self.entries = []
		self.selectionDiv = html5.Div()
		self.selectionDiv["class"].append("selectioncontainer")
		self.appendChild( self.selectionDiv )

		if ( "root" in conf[ "currentUser" ][ "access" ]
		     or destModul + "-view" in conf[ "currentUser" ][ "access" ] ):
			self.selectBtn = html5.ext.Button(translate("Select"), self.onShowSelector)
			self.selectBtn["class"].append("icon")
			self.selectBtn["class"].append("select")
			self.appendChild( self.selectBtn )
		else:
			self.selectBtn = None

		if self.readOnly:
			self["disabled"] = True

	def _setDisabled(self, disable):
		"""
			Reset the is_active flag (if any)
		"""
		super(RelationalMultiSelectionBone, self)._setDisabled( disable )
		if not disable and not self._disabledState and "is_active" in self.parent()["class"]:
			self.parent()["class"].remove("is_active")


	@classmethod
	def fromSkelStructure( cls, modulName, boneName, skelStructure ):
		"""
			Constructs a new RelationalMultiSelectionBone from the parameters given in skelStructure.
			@param modulName: Name of the modul which send us the skelStructure
			@type modulName: string
			@param boneName: Name of the bone which we shall handle
			@type boneName: string
			@param skelStructure: The parsed skeleton structure send by the server
			@type skelStructure: dict
		"""
		readOnly = "readonly" in skelStructure[ boneName ].keys() and skelStructure[ boneName ]["readonly"]
		multiple = skelStructure[boneName]["multiple"]
		if "modul" in skelStructure[ boneName ].keys():
			destModul = skelStructure[ boneName ][ "modul" ]
		else:
			destModul = skelStructure[ boneName ]["type"].split(".")[1]
		format= "$(name)"
		if "format" in skelStructure[ boneName ].keys():
			format = skelStructure[ boneName ]["format"]
		return( cls( modulName, boneName, readOnly, destModul=destModul, format=format ) )

	def unserialize(self, data):
		"""
			Parses the values received from the server and update our value accordingly.
			@param data: The data dictionary received.
			@type data: dict
		"""
		if self.boneName in data.keys():
			val = data[ self.boneName ]
			if isinstance( val, dict ):
				val = [ val ]
			self.setSelection( val )
			#self.setText( data[ self.boneName ] if data[ self.boneName ] else "" )
			#self.lineEdit.setText( str( data[ self.boneName ] ) if data[ self.boneName ] else "" )

	def serializeForPost(self):
		"""
			Serializes our values into something that can be transferred to the server using POST.
			@returns: dict
		"""
		return( { self.boneName: [x.data["key"] for x in self.entries]} )

	def serializeForDocument(self):
		return( self.serialize( ) )

	def onShowSelector(self, *args, **kwargs):
		"""
			Opens a ListWidget sothat the user can select new values
		"""
		currentSelector = ListWidget( self.destModul, isSelector=True )
		currentSelector.selectionActivatedEvent.register( self )
		conf["mainWindow"].stackWidget( currentSelector )
		self.parent()["class"].append("is_active")

	def onSelectionActivated(self, table, selection ):
		"""
			Merges the selection made in the ListWidget into our value(s)
		"""
		self.setSelection( selection )

	def setSelection(self, selection):
		"""
			Set our current value to 'selection'
			@param selection: The new entry that this bone should reference
			@type selection: dict
		"""
		print( selection )
		if selection is None:
			return
		for data in selection:
			entry = RelationalMultiSelectionBoneEntry( self, self.destModul, data, self.format)
			self.addEntry( entry )

	def addEntry(self, entry):
		"""
			Adds a new RelationalMultiSelectionBoneEntry to this bone.
			@type entry: RelationalMultiSelectionBoneEntry
		"""
		self.entries.append( entry )
		self.selectionDiv.appendChild( entry )

	def removeEntry(self, entry ):
		"""
			Removes a RelationalMultiSelectionBoneEntry from this bone.
			@type entry: RelationalMultiSelectionBoneEntry
		"""
		assert entry in self.entries, "Cannot remove unknown entry %s from realtionalBone" % str(entry)
		self.selectionDiv.removeChild( entry )
		self.entries.remove( entry )

	def onAttach(self):
		super( RelationalMultiSelectionBone,  self ).onAttach()
		NetworkService.registerChangeListener( self )

	def onDetach(self):
		NetworkService.removeChangeListener( self )
		super( RelationalMultiSelectionBone,  self ).onDetach()

	def onDataChanged(self, modul):
		if modul == self.destModul:
			selection = [ x.data for x in self.entries ]
			for e in self.entries[:]:
				self.removeEntry( e )
			self.setSelection( selection )

class ExtendedRelationalSearch( html5.Div ):
	def __init__(self, extension, view, modul, *args, **kwargs ):
		super( ExtendedRelationalSearch, self ).__init__( *args, **kwargs )
		self.view = view
		self.extension = extension
		self.modul = modul
		self.currentSelection = None
		self.filterChangedEvent = EventDispatcher("filterChanged")
		tmpSpan = html5.Span()
		tmpSpan.appendChild( html5.TextNode(extension["name"]))
		self.appendChild(tmpSpan)
		self.currentEntry = html5.Span()
		#self.appendChild(self.currentEntry) #FIXME: The selector is closed immediately after selecting an entity - you cant see it anyway
		btn = html5.ext.Button(translate("Select"), self.openSelector)
		btn["class"].append("icon select")
		self.appendChild( btn )
		btn = html5.ext.Button(translate("Clear"), self.clearSelection)
		btn["class"].append("icon cancel")
		self.appendChild( btn )

	def clearSelection(self, *args, **kwargs):
		self.currentSelection = None
		self.filterChangedEvent.fire()

	def openSelector(self, *args, **kwargs):
		currentSelector = ListWidget( self.extension["modul"], isSelector=True )
		currentSelector.selectionActivatedEvent.register( self )
		conf["mainWindow"].stackWidget( currentSelector )

	def onSelectionActivated(self, table,selection):
		self.currentSelection = selection
		self.filterChangedEvent.fire()


	def updateFilter(self, filter):
		if self.currentSelection:
			self.currentEntry.element.innerHTML = self.currentSelection[0]["name"]
			newId = self.currentSelection[0]["key"]
			filter[ self.extension["target"]+".id" ] = newId
		else:
			self.currentEntry.element.innerHTML = ""
		return( filter )

	@staticmethod
	def canHandleExtension( extension, view, modul ):
		return( isinstance( extension, dict) and "type" in extension.keys() and (extension["type"]=="relational" or extension["type"].startswith("relational.") ) )

def CheckForRelationalBoneSingleSelection( modulName, boneName, skelStructure, *args, **kwargs ):
	isMultiple = "multiple" in skelStructure[boneName].keys() and skelStructure[boneName]["multiple"]
	return CheckForRelationalBone( modulName, boneName, skelStructure ) and not isMultiple

def CheckForRelationalBoneMultiSelection( modulName, boneName, skelStructure, *args, **kwargs ):
	isMultiple = "multiple" in skelStructure[boneName].keys() and skelStructure[boneName]["multiple"]
	return CheckForRelationalBone( modulName, boneName, skelStructure ) and isMultiple

def CheckForRelationalBone(  modulName, boneName, skelStucture, *args, **kwargs ):
	return( skelStucture[boneName]["type"].startswith("relational.") )

#Register this Bone in the global queue
editBoneSelector.insert( 3, CheckForRelationalBoneSingleSelection, RelationalSingleSelectionBone)
editBoneSelector.insert( 3, CheckForRelationalBoneMultiSelection, RelationalMultiSelectionBone)
viewDelegateSelector.insert( 3, CheckForRelationalBone, RelationalViewBoneDelegate)
extendedSearchWidgetSelector.insert( 1, ExtendedRelationalSearch.canHandleExtension, ExtendedRelationalSearch )
extractorDelegateSelector.insert(3, CheckForRelationalBone, RelationalBoneExtractor)
