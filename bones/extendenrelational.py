#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import html5
from priorityqueue import editBoneSelector, viewDelegateSelector, extendedSearchWidgetSelector
from event import EventDispatcher
from utils import formatString
from widgets.list import ListWidget
from widgets.edit import InternalEdit
from config import conf


class ExtendedRelationalViewBoneDelegate( object ):
	cantSort = True
	def __init__(self, modul, boneName, structure):
		super(ExtendedRelationalViewBoneDelegate, self).__init__()
		self.format = "$(dest.name)"
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
		relStructList = self.structure[self.boneName]["using"]
		relStructDict = { k:v for k,v in relStructList }
		if isinstance(val,list):
			val = ", ".join( [ (formatString(formatString(self.format, self.structure, x["dest"], prefix=["dest"]), relStructDict, x["rel"], prefix=["rel"] ) or x["id"]) for x in val] )
		elif isinstance(val, dict):
			val = formatString(formatString(self.format,self.structure, val["dest"], prefix=["dest"]), relStructDict, val["rel"], prefix=["rel"] ) or val["id"]
		return( html5.Label( val ) )

class ExtendedRelationalSelectionBoneEntry( html5.Div ):
	"""
		Wrapper-class that holds one referenced entry in a RelationalMultiSelectionBone.
		Provides the UI to display its data and a button to remove it from the bone.
	"""

	def __init__(self, parent, modul, data, using, errorInfo, *args, **kwargs ):
		"""
			@param parent: Reference to the RelationalMultiSelectionBone we belong to
			@type parent: RelationalMultiSelectionBone
			@param modul: Name of the modul which references
			@type modul: String
			@param data: Values of the entry we shall display
			@type data: dict
		"""
		super( ExtendedRelationalSelectionBoneEntry, self ).__init__( *args, **kwargs )
		self.parent = parent
		self.modul = modul
		self.data = data
		if using and "dest" in data.keys():
			if "name" in data["dest"].keys():
				txtLbl = html5.Label( data["dest"]["name"])
			else:
				txtLbl = html5.Label( data["dest"]["id"])
		else:
			if "name" in data.keys():
				txtLbl = html5.Label( data["name"])
			else:
				txtLbl = html5.Label( data["id"])
		self.appendChild( txtLbl )
		remBtn = html5.ext.Button("Remove", self.onRemove )
		remBtn["class"].append("icon")
		remBtn["class"].append("cancel")
		if using:
			self.ie = InternalEdit( using, data["rel"],errorInfo )
			self.appendChild( self.ie )
		else:
			self.ie = None
		self.appendChild( remBtn )

	def onRemove(self, *args, **kwargs):
		self.parent.removeEntry( self )

	def serialize(self):
		if self.ie:
			res = {}
			res.update( self.ie.doSave() )
			res["id"] = self.data["dest"]["id"]
			return( res )
		else:
			return( self.data["id"] )


class ExtendedRelationalSelectionBone( html5.Div ):
	"""
		Provides the widget for a relationalBone with multiple=True
	"""

	def __init__(self, srcModul, boneName, readOnly, destModul, format="$(name)", using=None, *args, **kwargs ):
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
		print("---------- EXTENDED RELATIONAL SELECTION UP---------------")
		super( ExtendedRelationalSelectionBone,  self ).__init__( *args, **kwargs )
		#self["class"].append("relational")
		#self["class"].append("multiple")
		self.srcModul = srcModul
		self.boneName = boneName
		self.readOnly = readOnly
		self.destModul = destModul
		self.format = format
		self.using = using
		self.entries = []
		self.extendedErrorInformation = {}
		self.selectionDiv = html5.Div()
		self.selectionDiv["class"].append("selectioncontainer")
		self.appendChild( self.selectionDiv )
		self.selectBtn = html5.ext.Button("Select", self.onShowSelector)
		self.selectBtn["class"].append("icon")
		self.selectBtn["class"].append("select")
		self.appendChild( self.selectBtn )
		if self.readOnly:
			self["disabled"] = True

	def _setDisabled(self, disable):
		"""
			Reset the is_active flag (if any)
		"""
		super(ExtendedRelationalSelectionBone, self)._setDisabled( disable )
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
		using= None
		if "using" in skelStructure[ boneName ].keys():
			using = skelStructure[ boneName ]["using"]
		return( cls( modulName, boneName, readOnly, destModul=destModul, format=format, using=using ) )

	def unserialize(self, data):
		"""
			Parses the values received from the server and update our value accordingly.
			@param data: The data dictionary received.
			@type data: dict
		"""
		if self.boneName in data.keys():
			print("USERIALIZING", data[ self.boneName ])
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

		res = {}
		idx = 0
		for entry in self.entries:
			currRes = entry.serialize()
			if isinstance( currRes, dict ):
				for k,v in currRes.items():
					res["%s%s.%s" % (self.boneName,idx,k) ] = v
			else:
				res["%s%s.id" % (self.boneName,idx) ] = currRes
			idx += 1
		return( res )
		#return( { self.boneName: [x.data["id"] for x in self.entries]} )

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
		if self.using:
			selection = [{"dest": data,"rel":{}} for data in selection]
		self.setSelection( selection )

	def setSelection(self, selection):
		"""
			Set our current value to 'selection'
			@param selection: The new entry that this bone should reference
			@type selection: dict
		"""
		if selection is None:
			return
		for data in selection:
			errIdx = len( self. entries )
			errDict = {}
			if self.extendedErrorInformation:
				for k,v in self.extendedErrorInformation.items():
					k = k.replace("%s." % self.boneName, "")
					if 1:
						idx, errKey = k.split(".")
						idx = int( idx )
					else:
						continue
					if idx == errIdx:
						errDict[ errKey ] = v
			entry = ExtendedRelationalSelectionBoneEntry( self, self.destModul, data, self.using, errDict )
			self.addEntry( entry )

	def addEntry(self, entry):
		"""
			Adds a new RelationalMultiSelectionBoneEntry to this bone.
			@type entry: RelationalMultiSelectionBoneEntry
		"""
		print("--adding entry--")
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

	def setExtendedErrorInformation(self, errorInfo ):
		print("------- EXTENDEND ERROR INFO --------")
		print( errorInfo )
		self.extendedErrorInformation = errorInfo
		for k,v in errorInfo.items():
			k = k.replace("%s." % self.boneName, "")
			if 1:
				idx, err = k.split(".")
				idx = int( idx )
			else:
				continue
			print("k: %s, v: %s" % (k,v))
			print("idx: %s" % idx )
			print( len(self.entries))
			if idx>=0 and idx < len(self.entries):
				self.entries[ idx ].setError( err )
		pass


class ExtendedRelationalSearch( html5.Div ):
	def __init__(self, extension, view, modul, *args, **kwargs ):
		super( ExtendedRelationalSearch, self ).__init__( *args, **kwargs )
		self.view = view
		self.extension = extension
		self.modul = modul
		self.currentSelection = None
		self.filterChangedEvent = EventDispatcher("filterChanged")
		self.appendChild( html5.TextNode("RELATIONAL SEARCH"))
		self.appendChild( html5.TextNode(extension["name"]))
		self.currentEntry = html5.Span()
		self.appendChild(self.currentEntry)
		btn = html5.ext.Button("Select", self.openSelector)
		self.appendChild( btn )
		btn = html5.ext.Button("Clear", self.clearSelection)
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
			newId = self.currentSelection[0]["id"]
			filter[ self.extension["target"]+".id" ] = newId
		else:
			self.currentEntry.element.innerHTML = ""
		return( filter )

	@staticmethod
	def canHandleExtension( extension, view, modul ):
		return( isinstance( extension, dict) and "type" in extension.keys() and (extension["type"]=="relational" or extension["type"].startswith("relational.") ) )


def CheckForExtendedRelationalBoneSelection( modulName, boneName, skelStructure, *args, **kwargs ):
	isMultiple = "multiple" in skelStructure[boneName].keys() and skelStructure[boneName]["multiple"]
	return( skelStructure[boneName]["type"].startswith("extendedrelational.") and isMultiple )



#Register this Bone in the global queue
editBoneSelector.insert( 5, CheckForExtendedRelationalBoneSelection, ExtendedRelationalSelectionBone)
viewDelegateSelector.insert( 5, CheckForExtendedRelationalBoneSelection, ExtendedRelationalViewBoneDelegate)
extendedSearchWidgetSelector.insert( 1, ExtendedRelationalSearch.canHandleExtension, ExtendedRelationalSearch )
