#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import html5
from priorityqueue import editBoneSelector, viewDelegateSelector
from utils import formatString
from widgets.list import ListWidget
from config import conf


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
			val = ", ".join( [(x["name"] if "name" in x.keys() else x["id"]) for x in val])
		elif isinstance(val, dict):
			val = val["name"] if "name" in val.keys() else val["id"]
		return( html5.Label( val ) )
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
		self.selectionTxt._setReadonly(True)
		self.appendChild( self.selectionTxt )
		#DOM.setElemAttribute( self.selectionTxt, "type", "text")
		#DOM.appendChild(self.getElement(), self.selectionTxt )
		self.selectBtn = html5.ext.Button("Select", self.onShowSelector)
		self.selectBtn["class"].append("icon")
		self.selectBtn["class"].append("select")
		self.appendChild( self.selectBtn )
		if not required:
			remBtn = html5.ext.Button("Remove", self.onRemove )
			remBtn["class"].append("icon")
			remBtn["class"].append("cancel")
			self.appendChild( remBtn )
		#DOM.appendChild( self.getElement(), self.selectBtn.getElement())
		#self.selectBtn.onAttach()

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

	def onRemove(self, *args, **kwargs):
		self.setSelection( None )

	def unserialize(self, data):
		"""
			Parses the values received from the server and update our value accordingly.
			@param data: The data dictionary received.
			@type data: dict
		"""
		if self.boneName in data.keys():
			print("USERIALIZING", data[ self.boneName ])
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
		return( { self.boneName: self.selection["id"] if self.selection is not None else "" } )

	def serializeForDocument(self):
		return( self.serialize( ) )

	def onShowSelector(self, *args, **kwargs):
		"""
			Opens a ListWidget sothat the user can select new values
		"""
		currentSelector = ListWidget( self.destModul, isSelector=True )
		currentSelector.selectionActivatedEvent.register( self )
		conf["mainWindow"].stackWidget( currentSelector )

	def onSelectionActivated(self, table, selection ):
		"""
			Merges the selection made in the ListWidget into our value(s)
		"""
		print("GOT NEW SELECTION", selection)
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
			if "name" in selection.keys():
				self.selectionTxt["value"] = selection["name"]
			else:
				self.selectionTxt["value"] = selection["id"]
		else:
			self.selectionTxt["value"] = ""

class RelationalMultiSelectionBoneEntry( html5.Div ):
	"""
		Wrapper-class that holds one referenced entry in a RelationalMultiSelectionBone.
		Provides the UI to display its data and a button to remove it from the bone.
	"""

	def __init__(self, parent, modul, data, *args, **kwargs ):
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
		if "name" in data.keys():
			txtLbl = html5.Label( data["name"])
		else:
			txtLbl = html5.Label( data["id"])
		self.appendChild( txtLbl )
		remBtn = html5.ext.Button("Remove", self.onRemove )
		remBtn["class"].append("icon")
		remBtn["class"].append("cancel")
		self.appendChild( remBtn )

	def onRemove(self, *args, **kwargs):
		self.parent.removeEntry( self )


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
		self.selectBtn = html5.ext.Button("Select", self.onShowSelector)
		self.selectBtn["class"].append("icon")
		self.selectBtn["class"].append("select")
		self.appendChild( self.selectBtn )


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
		return( { self.boneName: [x.data["id"] for x in self.entries]} )

	def serializeForDocument(self):
		return( self.serialize( ) )

	def onShowSelector(self, *args, **kwargs):
		"""
			Opens a ListWidget sothat the user can select new values
		"""
		currentSelector = ListWidget( self.destModul, isSelector=True )
		currentSelector.selectionActivatedEvent.register( self )
		conf["mainWindow"].stackWidget( currentSelector )

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
			entry = RelationalMultiSelectionBoneEntry( self, self.destModul, data)
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

def CheckForRelationalBoneSingleSelection( modulName, boneName, skelStructure ):
	isMultiple = "multiple" in skelStructure[boneName].keys() and skelStructure[boneName]["multiple"]
	return CheckForRelationalBone( modulName, boneName, skelStructure ) and not isMultiple

def CheckForRelationalBoneMultiSelection( modulName, boneName, skelStructure ):
	isMultiple = "multiple" in skelStructure[boneName].keys() and skelStructure[boneName]["multiple"]
	return CheckForRelationalBone( modulName, boneName, skelStructure ) and isMultiple

def CheckForRelationalBone(  modulName, boneName, skelStucture ):
	return( skelStucture[boneName]["type"].startswith("relational.") )

#Register this Bone in the global queue
editBoneSelector.insert( 3, CheckForRelationalBoneSingleSelection, RelationalSingleSelectionBone)
editBoneSelector.insert( 3, CheckForRelationalBoneMultiSelection, RelationalMultiSelectionBone)
viewDelegateSelector.insert( 3, CheckForRelationalBone, RelationalViewBoneDelegate)
