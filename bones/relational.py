# -*- coding: utf-8 -*-

import html5
from priorityqueue import editBoneSelector, viewDelegateSelector, extendedSearchWidgetSelector, extractorDelegateSelector
from event import EventDispatcher
from utils import formatString
from widgets.list import ListWidget
from widgets.edit import InternalEdit, EditWidget
from config import conf
from i18n import translate
from network import NetworkService
from pane import Pane


class RelationalBoneExtractor( object ):
	cantSort = True
	def __init__(self, modul, boneName, structure):
		super(RelationalBoneExtractor, self).__init__()
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
		try:
			if isinstance(val,list):
				val = ", ".join( [ (formatString(formatString(self.format, self.structure, x["dest"], prefix=["dest"]), relStructDict, x["rel"], prefix=["rel"] ) or x["key"]) for x in val] )
			elif isinstance(val, dict):
				val = formatString(formatString(self.format,self.structure, val["dest"], prefix=["dest"]), relStructDict, val["rel"], prefix=["rel"] ) or val["key"]
		except:
			#We probably received some garbage
			val = ""
		return val


class RelationalViewBoneDelegate( object ):
	cantSort = True
	def __init__(self, modul, boneName, structure):
		super(RelationalViewBoneDelegate, self).__init__()
		self.format = "$(dest.name)"
		if "format" in structure[boneName].keys():
			self.format = structure[boneName]["format"]
		self.modul = modul
		self.structure = structure
		self.boneName = boneName

	def render(self, data, field ):
		assert field == self.boneName, "render() was called with field %s, expected %s" % (field,self.boneName)
		val = data.get(field, "")

		relStructList = relStructDict = self.structure[self.boneName].get("using")
		if relStructList:
			relStructDict = {k:v for k,v in relStructList}

		try:
			if isinstance(val, list):
				count = len(val)
				if count >= 5:
					val = val[:4]

				if relStructList:
					res = ", ".join( [ (formatString(formatString(self.format, self.structure, x["dest"], prefix=["dest"]), relStructDict, x["rel"], prefix=["rel"] ) or x["key"]) for x in val])
				else:
					res = ", ".join( [ (formatString(self.format, self.structure, x ) or x["key"]) for x in val] )

				if count >= 5:
					res += " %s" % translate("and {count} more", count=count - 4)

			elif isinstance(val, dict):
				if relStructList:
					res = formatString(formatString(self.format,self.structure, val["dest"], prefix=["dest"]), relStructDict, val["rel"], prefix=["rel"] ) or val["key"]
				else:
					res = formatString(self.format, self.structure, val["dest"]) or val["dest"]["key"]

		except:
			#We probably received some garbage
			res = ""

		return html5.Label(res)

class RelationalMultiSelectionBoneEntry( html5.Div ):
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
		super( RelationalMultiSelectionBoneEntry, self ).__init__( *args, **kwargs )
		self.parent = parent
		self.modul = modul
		self.data = data
		if "dest" in data.keys():
			if "name" in data["dest"].keys():
				txtLbl = html5.Label( data["dest"]["name"])
			else:
				txtLbl = html5.Label( data["dest"]["key"])
		else:
			if "name" in data.keys():
				txtLbl = html5.Label( data["name"])
			else:
				try:
					txtLbl = html5.Label( data["key"])
				except KeyError:
					print("Received garbarge from sever!")
					txtLbl = html5.Label("Invalid data received")
		wrapperDiv = html5.Div()
		wrapperDiv.appendChild( txtLbl )
		wrapperDiv["class"].append("labelwrapper")

		if not parent.readOnly:
			remBtn = html5.ext.Button(translate("Remove"), self.onRemove )
			remBtn["class"].append("icon")
			remBtn["class"].append("cancel")
			wrapperDiv.appendChild( remBtn )

		self.appendChild( wrapperDiv )

		if using:
			self.ie = InternalEdit( using, data["rel"], errorInfo, readOnly = parent.readOnly )
			self.appendChild( self.ie )
		else:
			self.ie = None


	def onRemove(self, *args, **kwargs):
		self.parent.removeEntry( self )

	def serialize(self):
		if self.ie:
			res = {}
			res.update( self.ie.doSave() )
			res["key"] = self.data["dest"]["key"]
			return res
		else:
			return {"key": self.data["dest"]["key"]}


class RelationalSingleSelectionBone( html5.Div ):
	"""
		Provides the widget for a relationalBone with multiple=False
	"""

	def __init__(self, srcModul, boneName, readOnly, destModul, format="$(name)", required=False, using=None, *args, **kwargs ):
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
		self.using = using
		self.selection = None
		self.selectionTxt = html5.Input()
		self.selectionTxt["type"] = "text"
		self.selectionTxt["readonly"] = True
		self.appendChild( self.selectionTxt )
		self.ie = None
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
		if "module" in skelStructure[ boneName ].keys():
			destModul = skelStructure[ boneName ][ "module" ]
		else:
			destModul = skelStructure[ boneName ]["type"].split(".")[1]
		format= "$(name)"
		if "format" in skelStructure[ boneName ].keys():
			format = skelStructure[ boneName ]["format"]
		if "using" in skelStructure[ boneName ].keys() and skelStructure[ boneName ]["using"]:
			using = skelStructure[ boneName ]["using"]
		else:
			using = None
		return cls( modulName, boneName, readOnly, destModul=destModul, format=format, required=required, using=using )

	def onEdit(self, *args, **kwargs):
		"""
			Edit the reference.
		"""
		if not self.selection:
			return

		pane = Pane( translate("Edit"), closeable=True, iconClasses=[ "modul_%s" % self.destModul,
		                                                                    "apptype_list", "action_edit" ] )
		conf["mainWindow"].stackPane( pane, focus=True )

		try:
			edwg = EditWidget( self.destModul, EditWidget.appList, key=self.selection[ "key" ] )
			pane.addWidget( edwg )
		except AssertionError:
			conf["mainWindow"].removePane(pane)

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
				if self.using:
					if self.ie:
						self.removeChild(self.ie)
					self.ie = InternalEdit( self.using, val["rel"], {}, readOnly=self.readOnly )
					self.appendChild( self.ie )
			else:
				self.setSelection( None )

			#self.setText( data[ self.boneName ] if data[ self.boneName ] else "" )
			#self.lineEdit.setText( str( data[ self.boneName ] ) if data[ self.boneName ] else "" )

	def serializeForPost(self):
		"""
			Serializes our value into something that can be transferred to the server using POST.
			@returns: dict
		"""
		if not (self.selection and "dest" in self.selection.keys() and "key" in self.selection["dest"].keys()):
			# We have no value selected
			return {}
		res = {}
		if self.ie:
			res.update(self.ie.doSave())
		res["key"] = self.selection["dest"]["key"]
		r = {"%s0.%s" % (self.boneName, k): v for (k,v ) in res.items()}
		return r
		#return { self.boneName+".dest": self.selection["dest"]["key"], self.boneName+".rel": self.ie.doSave} if self.selection is not None else {}

	def serializeForDocument(self):
		return( self.serialize( ) )

	def onShowSelector(self, *args, **kwargs):
		"""
			Opens a ListWidget so that the user can select new values
		"""

		try:
			currentSelector = ListWidget( self.destModul, isSelector=True )
		except AssertionError:
			return

		currentSelector.selectionActivatedEvent.register( self )
		conf["mainWindow"].stackWidget( currentSelector )
		self.parent()["class"].append("is_active")

	def onSelectionActivated(self, table, selection ):
		"""
			Merges the selection made in the ListWidget into our value(s)
		"""
		if selection:
			self.setSelection({"dest": selection[0]})
		else:
			self.setSelection(None)

	def setSelection(self, selection):
		"""
			Set our current value to 'selection'
			@param selection: The new entry that this bone should reference
			@type selection: dict
		"""
		if not selection:
			self.selection = None
			return
		if not self.selection:
			self.selection = {}
		self.selection.update(selection)
		#self.selection["dest"] = selection
		if selection:
			NetworkService.request( self.destModul, "view/"+selection["dest"]["key"],
			                            successHandler=self.onSelectionDataAviable, cacheable=True)
			self.selectionTxt["value"] = translate("Loading...")
			if self.using and not self.ie:
				self.ie = InternalEdit( self.using,{}, {}, readOnly=self.readOnly )
				self.appendChild( self.ie )
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
		assert self.selection["dest"]["key"]==data["values"]["key"]
		self.selectionTxt["value"] = formatString( self.format ,data["structure"],data["values"] )

class RelationalMultiSelectionBone( html5.Div ):
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
		super( RelationalMultiSelectionBone,  self ).__init__( *args, **kwargs )
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

		if ( "root" in conf[ "currentUser" ][ "access" ]
		     or destModul + "-view" in conf[ "currentUser" ][ "access" ] ):
			self.selectBtn = html5.ext.Button("Select", self.onShowSelector)
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
			val = data[ self.boneName ]
			if isinstance( val, dict ):
				val = [ val ]
			self.setSelection( val )

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
				res["%s%s.key" % (self.boneName,idx) ] = currRes
			idx += 1
		return( res )
		#return( { self.boneName: [x.data["key"] for x in self.entries]} )

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
			entry = RelationalMultiSelectionBoneEntry( self, self.destModul, data, self.using, errDict )
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


class RelationalSearch( html5.Div ):
	def __init__(self, extension, view, modul, *args, **kwargs ):
		super( RelationalSearch, self ).__init__( *args, **kwargs )
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
			newId = self.currentSelection[0]["key"]
			filter[ self.extension["target"]+".key" ] = newId
		else:
			self.currentEntry.element.innerHTML = ""
		return( filter )

	@staticmethod
	def canHandleExtension( extension, view, modul ):
		return( isinstance( extension, dict) and "type" in extension.keys() and (extension["type"]=="relational" or extension["type"].startswith("relational.") ) )


def CheckForRelationalBoneSelection( modulName, boneName, skelStructure, *args, **kwargs ):
	return skelStructure[boneName]["type"].startswith("relational.")

def CheckForRelationalBoneMultiSelection( modulName, boneName, skelStructure, *args, **kwargs ):
	isMultiple = "multiple" in skelStructure[boneName].keys() and skelStructure[boneName]["multiple"]
	return isMultiple and skelStructure[boneName]["type"].startswith("relational.")

def CheckForRelationalBoneSingleSelection( modulName, boneName, skelStructure, *args, **kwargs ):
	isMultiple = "multiple" in skelStructure[boneName].keys() and skelStructure[boneName]["multiple"]
	return not isMultiple and skelStructure[boneName]["type"].startswith("relational.")

#Register this Bone in the global queue
editBoneSelector.insert( 5, CheckForRelationalBoneMultiSelection, RelationalMultiSelectionBone)
editBoneSelector.insert( 5, CheckForRelationalBoneSingleSelection, RelationalSingleSelectionBone)
viewDelegateSelector.insert( 5, CheckForRelationalBoneSelection, RelationalViewBoneDelegate)
extendedSearchWidgetSelector.insert( 1, RelationalSearch.canHandleExtension, RelationalSearch )
extractorDelegateSelector.insert(4, CheckForRelationalBoneSelection, RelationalBoneExtractor)
