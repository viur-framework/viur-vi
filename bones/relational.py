# -*- coding: utf-8 -*-
import html5, json, utils
from priorityqueue import editBoneSelector, viewDelegateSelector, extendedSearchWidgetSelector, extractorDelegateSelector
from event import EventDispatcher
from widgets.list import ListWidget
from widgets.edit import InternalEdit, EditWidget
from config import conf
from i18n import translate
from network import NetworkService
from pane import Pane
from bones.base import BaseBoneExtractor

def getDefaultValues(structure):
	defaultValues = {}
	for k, v in {k: v for k, v in structure}.items():
		if "params" in v.keys() and v["params"] and "defaultValue" in v["params"].keys():
			defaultValues[k] = v["params"]["defaultValue"]

	return defaultValues

class RelationalBoneExtractor(BaseBoneExtractor):
	def __init__(self, module, boneName, structure):
		super(RelationalBoneExtractor, self).__init__()
		self.format = "$(dest.name)"

		if "format" in structure[boneName].keys():
			self.format = structure[boneName]["format"]

		self.module = module
		self.structure = structure
		self.boneName = boneName

	def render(self, data, field ):
		assert field == self.boneName, "render() was called with field %s, expected %s" % (field, self.boneName)

		if field in data.keys():
			val = data[field]
		else:
			val = ""

		structure = self.structure[self.boneName]

		try:
			if not isinstance(val, list):
				val = [val]

			val = ", ".join([(utils.formatString(
								utils.formatString(self.format, x["dest"], structure["relskel"],
								                    prefix=["dest"], language=conf["currentlanguage"]),
									x["rel"], structure["using"],
										prefix=["rel"], language=conf["currentlanguage"])
			                    or x["key"]) for x in val])
		except:
			#We probably received some garbage
			print("Cannot build relational format, maybe garbage received?")
			print(val)
			val = ""

		return val

	def raw(self, data, field):
		assert field == self.boneName, "render() was called with field %s, expected %s" % (field, self.boneName)

		if not field in data.keys():
			return None

		val = data[field]
		structure = self.structure[self.boneName]

		try:
			if not isinstance(val, list):
				val = [val]

			val = [(utils.formatString(
								utils.formatString(self.format, x["dest"], structure["relskel"],
								                    prefix=["dest"], language=conf["currentlanguage"]),
									x["rel"], structure["using"],
										prefix=["rel"], language=conf["currentlanguage"])
			                    or x["key"]) for x in val]
		except:
			#We probably received some garbage
			print("Cannot build relational format, maybe garbage received?")
			print(val)
			return None

		return val[0] if len(val) == 1 else val

class RelationalViewBoneDelegate(object):

	def __init__(self, module, boneName, structure):
		super(RelationalViewBoneDelegate, self).__init__()
		self.format = "$(dest.name)"

		if "format" in structure[boneName].keys():
			self.format = structure[boneName]["format"]

		self.module = module
		self.structure = structure
		self.boneName = boneName

	def render(self, data, field):
		assert field == self.boneName, "render() was called with field %s, expected %s" % (field, self.boneName)
		val = data.get(field, "")

		structure = self.structure[self.boneName]

		lbl = html5.Label()

		if not val:
			return lbl

		try:
			if not isinstance(val, list):
				val = [val]
				count = 1
			else:
				count = len(val)
				if conf["maxMultiBoneEntries"] and count >= conf["maxMultiBoneEntries"]:
					val = val[:conf["maxMultiBoneEntries"] - 1]

			if structure["using"]:
				res = "\n".join([(utils.formatString(
									utils.formatString(self.format, x["dest"], structure["relskel"],
									                    prefix=["dest"], language=conf["currentlanguage"]),
										x["rel"], structure["using"],
											prefix=["rel"], language=conf["currentlanguage"])
				                  or x["key"]) for x in val])
			else:
				res = "\n".join([(utils.formatString(
									utils.formatString(self.format, x["dest"], structure["relskel"],
									                    prefix=["dest"], language=conf["currentlanguage"]),
														x["dest"], structure["relskel"],
															language=conf["currentlanguage"])
				                  or x["key"]) for x in val])

			if conf["maxMultiBoneEntries"] and count >= conf["maxMultiBoneEntries"]:
				res += "\n%s" % translate("and {count} more", count=count - conf["maxMultiBoneEntries"] - 1)

		except:
			#We probably received some garbage
			print("Cannot build relational format, maybe garbage received?")
			print(val)

			res = ""

		html5.utils.textToHtml(lbl, res)
		return lbl


class RelationalSingleSelectionBone(html5.Div):
	"""
		Provides the widget for a relationalBone with multiple=False
	"""

	def __init__(self, srcModule, boneName, readOnly, destModule, format="$(dest.name)", required=False,
	                using = None, usingDescr = None, *args, **kwargs ):
		"""
			@param srcModule: Name of the module from which is referenced
			@type srcModule: string
			@param boneName: Name of the bone thats referencing
			@type boneName: string
			@param readOnly: Prevents modifying its value if set to True
			@type readOnly: bool
			@param destModule: Name of the module which gets referenced
			@type destModule: string
			@param format: Specifies how entries should be displayed.
			@type format: string
		"""
		super( RelationalSingleSelectionBone,  self ).__init__( *args, **kwargs )
		self.srcModule = srcModule
		self.boneName = boneName
		self.readOnly = readOnly
		self.destModule = destModule
		self.format = format
		self.using = using
		self.usingDescr = usingDescr

		self.selection = None
		self.selectionTxt = html5.Input()
		self.selectionTxt["type"] = "text"
		self.selectionTxt["readonly"] = True
		self.appendChild( self.selectionTxt )
		self.ie = None

		# Selection button
		if (destModule in conf["modules"].keys()
			and ("root" in conf["currentUser"]["access"] or destModule + "-view" in conf["currentUser"]["access"])):

			self.selectBtn = html5.ext.Button(translate("Select"), self.onShowSelector)
			self.selectBtn["class"].append("icon")
			self.selectBtn["class"].append("select")
			self.appendChild( self.selectBtn )
		else:
			self.selectBtn = None

		# Edit button
		if (destModule in conf["modules"].keys()
			and ("root" in conf["currentUser"]["access"] or destModule + "-edit" in conf["currentUser"]["access"])):
			self.editBtn = html5.ext.Button(translate("Edit"), self.onEdit )
			self.editBtn["class"].append("icon")
			self.editBtn["class"].append("edit")
			self.appendChild( self.editBtn )
		else:
			self.editBtn = None

		# Remove button
		if (not required and not readOnly
		    and ("root" in conf["currentUser"]["access"]
		            or destModule + "-view" in conf["currentUser"]["access"])):
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

	def _setDisabled(self, disable):
		"""
			Reset the is_active flag (if any)
		"""
		super(RelationalSingleSelectionBone, self)._setDisabled( disable )
		if not disable and not self._disabledState and "is_active" in self.parent()["class"]:
			self.parent()["class"].remove("is_active")

	@classmethod
	def fromSkelStructure( cls, moduleName, boneName, skelStructure ):
		"""
			Constructs a new RelationalSingleSelectionBone from the parameters given in skelStructure.
			@param moduleName: Name of the module which send us the skelStructure
			@type moduleName: string
			@param boneName: Name of the bone which we shall handle
			@type boneName: string
			@param skelStructure: The parsed skeleton structure send by the server
			@type skelStructure: dict
		"""
		readOnly = "readonly" in skelStructure[ boneName ].keys() and skelStructure[ boneName ]["readonly"]

		if "required" in skelStructure[boneName].keys() and skelStructure[boneName]["required"]:
			required = True
		else:
			required = False

		if "module" in skelStructure[boneName].keys():
			destModule = skelStructure[boneName]["module"]
		else:
			destModule = skelStructure[boneName]["type"].split(".")[1]

		format = "$(name)"
		if "format" in skelStructure[ boneName ].keys():
			format = skelStructure[ boneName ]["format"]

		if "using" in skelStructure[ boneName ].keys() and skelStructure[ boneName ]["using"]:
			using = skelStructure[ boneName ]["using"]
		else:
			using = None

		if ("params" in skelStructure[boneName].keys()
		    and skelStructure[boneName]["params"]
			and "usingDescr" in skelStructure[boneName]["params"].keys()):
			usingDescr = skelStructure[boneName]["params"]["usingDescr"]
		else:
			usingDescr = skelStructure[boneName].get("descr", boneName)

		return cls(moduleName, boneName, readOnly, destModule=destModule,
		            format=format, required=required, using=using, usingDescr=usingDescr)

	def onEdit(self, *args, **kwargs):
		"""
			Edit the reference.
		"""
		if not self.selection:
			return

		pane = Pane(translate("Edit"), closeable=True,
		            iconClasses=["module_%s" % self.destModule, "apptype_list", "action_edit"])
		conf["mainWindow"].stackPane( pane, focus=True )

		try:
			edwg = EditWidget(self.destModule, EditWidget.appList, key=self.selection["dest"]["key"])
			pane.addWidget(edwg)

		except AssertionError:
			conf["mainWindow"].removePane(pane)

	def onRemove(self, *args, **kwargs):
		self.setSelection(None)

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

					print("2 WITH ", data["rel"])

					self.ie = InternalEdit(self.using, val["rel"], {},
					                        readOnly=self.readOnly, defaultCat=self.usingDescr)
					self.appendChild( self.ie )
			else:
				self.setSelection(None)

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
		r = {"%s.0.%s" % (self.boneName, k): v for (k,v ) in res.items()}
		return r
		#return { self.boneName+".dest": self.selection["dest"]["key"], self.boneName+".rel": self.ie.doSave} if self.selection is not None else {}

	def serializeForDocument(self):
		return self.serialize()

	def onShowSelector(self, *args, **kwargs):
		"""
			Opens a ListWidget so that the user can select new values
		"""

		try:
			currentSelector = ListWidget( self.destModule, isSelector=True )
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
			selection = {}
			self.selection = None

		if not self.selection:
			self.selection = {}

		self.selection.update(selection)

		if selection:
			NetworkService.request(self.destModule, "view/%s" % selection["dest"]["key"],
			                        successHandler=self.onSelectionDataAvailable, cacheable=True)

			self.selectionTxt["value"] = translate("Loading...")

			if self.using and not self.ie:
				self.ie = InternalEdit(self.using, getDefaultValues(self.using), {},
				                        readOnly=self.readOnly, defaultCat=self.usingDescr)
				self.appendChild(self.ie)
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
		super(RelationalSingleSelectionBone, self).onAttach()
		NetworkService.registerChangeListener(self)

	def onDetach(self):
		NetworkService.removeChangeListener(self)
		super(RelationalSingleSelectionBone, self).onDetach()

	def onDataChanged(self, module, **kwargs):
		if module == self.destModule:
			self.setSelection(self.selection)

	def onSelectionDataAvailable(self, req):
		"""
			We just received the full information for this entry from the server and can start displaying it
		"""
		data = NetworkService.decode(req)
		assert self.selection["dest"]["key"] == data["values"]["key"]

		if self.using:
			res = (utils.formatString(
					utils.formatString(self.format, data["values"], data["structure"],
					                    prefix=["dest"], language=conf["currentlanguage"]),
							self.selection["rel"], self.using,
								prefix=["rel"], language=conf["currentlanguage"])
		                or data["values"]["key"])
		else:
			res = (utils.formatString(
					utils.formatString(self.format, data["values"], data["structure"],
					                    prefix=["dest"], language=conf["currentlanguage"]),
						data["values"], data["structure"], language=conf["currentlanguage"])
			                or data["values"]["key"])

		self.selectionTxt["value"] = res

class RelationalMultiSelectionBoneEntry(html5.Div):
	"""
		Wrapper-class that holds one referenced entry in a RelationalMultiSelectionBone.
		Provides the UI to display its data and a button to remove it from the bone.
	"""

	def __init__(self, parent, module, data, using, errorInfo, *args, **kwargs ):
		"""
			@param parent: Reference to the RelationalMultiSelectionBone we belong to
			@type parent: RelationalMultiSelectionBone
			@param module: Name of the module which references
			@type module: String
			@param data: Values of the entry we shall display
			@type data: dict
		"""
		super(RelationalMultiSelectionBoneEntry, self).__init__(*args, **kwargs)

		self["draggable"] = not parent.readOnly
		self.sinkEvent("onDrop", "onDragOver", "onDragStart", "onDragEnd", "onChange")

		self.parent = parent
		self.module = module
		self.data = data

		self.txtLbl = html5.Label()

		wrapperDiv = html5.Div()
		wrapperDiv.appendChild(self.txtLbl)
		wrapperDiv["class"].append("labelwrapper")

		if not parent.readOnly:
			remBtn = html5.ext.Button(translate("Remove"), self.onRemove)
			remBtn["class"].append("icon")
			remBtn["class"].append("cancel")
			wrapperDiv.appendChild(remBtn)

		self.appendChild(wrapperDiv)

		if using:
			print("1 WITH ",data["rel"])
			self.ie = InternalEdit(using, data["rel"], errorInfo,
			                        readOnly = parent.readOnly,
			                        defaultCat = parent.usingDescr)
			self.appendChild(self.ie)
		else:
			self.ie = None

		self.updateLabel()

	def updateLabel(self, data = None):
		if data is None:
			data = self.data

		self.txtLbl.removeAllChildren()
		txt = utils.formatString(self.parent.format, data["dest"], self.parent.relskel,
		                            prefix=["dest"], language=conf["currentlanguage"])

		if self.ie:
			txt = utils.formatString(txt, self.ie.doSave(), self.parent.using,
			                            prefix=["rel"], language=conf["currentlanguage"])

		html5.utils.textToHtml(self.txtLbl, txt)

	def onDragStart(self, event):
		if self.parent.readOnly:
			return

		self.parent.currentDrag = self
		event.dataTransfer.setData("application/json", json.dumps(self.data))
		event.stopPropagation()

	def onDragOver(self, event):
		if self.parent.readOnly:
			return

		event.preventDefault()

	def onDragEnd(self, event):
		if self.parent.readOnly:
			return

		self.parent.currentDrag = None
		event.stopPropagation()

	def onDrop(self, event):
		if self.parent.readOnly:
			return

		event.preventDefault()
		event.stopPropagation()

		if self.parent.currentDrag and self.parent.currentDrag != self:
			if self.element.offsetTop > self.parent.currentDrag.element.offsetTop:
				if self.parent.entries[-1] is self:
					self.parent.moveEntry(self.parent.currentDrag)
				else:
					self.parent.moveEntry(self.parent.currentDrag, self.parent.entries[self.parent.entries.index(self) + 1])
			else:
				self.parent.moveEntry(self.parent.currentDrag, self)

		self.parent.currentDrag = None

	def onChange(self, event):
		data = self.data.copy()
		data["rel"].update(self.ie.doSave())

		self.updateLabel(data)

	def onRemove(self, *args, **kwargs):
		self.parent.removeEntry(self)

	def serialize(self):
		if self.ie:
			res = {}
			res.update(self.ie.doSave())
			res["key"] = self.data["dest"]["key"]
			return res
		else:
			return {"key": self.data["dest"]["key"]}


class RelationalMultiSelectionBone(html5.Div):
	"""
		Provides the widget for a relationalBone with multiple=True
	"""

	def __init__(self, srcModule, boneName, readOnly, destModule, format="$(name)", using=None, usingDescr=None,
	                relskel=None, *args, **kwargs ):
		"""
			@param srcModule: Name of the module from which is referenced
			@type srcModule: string
			@param boneName: Name of the bone thats referencing
			@type boneName: string
			@param readOnly: Prevents modifying its value if set to True
			@type readOnly: bool
			@param destModule: Name of the module which gets referenced
			@type destModule: string
			@param format: Specifies how entries should be displayed.
			@type format: string
		"""
		super( RelationalMultiSelectionBone,  self ).__init__( *args, **kwargs )

		self.srcModule = srcModule
		self.boneName = boneName
		self.readOnly = readOnly
		self.destModule = destModule
		self.format = format
		self.using = using
		self.usingDescr = usingDescr
		self.relskel = relskel

		self.entries = []
		self.extendedErrorInformation = {}
		self.currentDrag = None

		self.selectionDiv = html5.Div()
		self.selectionDiv["class"].append("selectioncontainer")
		self.appendChild(self.selectionDiv)

		if (destModule in conf["modules"].keys()
			and ("root" in conf["currentUser"]["access"] or destModule + "-view" in conf["currentUser"]["access"])):

			self.selectBtn = html5.ext.Button("Select", self.onShowSelector)
			self.selectBtn["class"].append("icon")
			self.selectBtn["class"].append("select")
			self.appendChild( self.selectBtn )
		else:
			self.selectBtn = None

		if self.readOnly:
			self["disabled"] = True

		self.sinkEvent("onDragOver")

	def _setDisabled(self, disable):
		"""
			Reset the is_active flag (if any)
		"""
		super(RelationalMultiSelectionBone, self)._setDisabled( disable )
		if not disable and not self._disabledState and "is_active" in self.parent()["class"]:
			self.parent()["class"].remove("is_active")

	@classmethod
	def fromSkelStructure( cls, moduleName, boneName, skelStructure ):
		"""
			Constructs a new RelationalMultiSelectionBone from the parameters given in skelStructure.
			@param moduleName: Name of the module which send us the skelStructure
			@type moduleName: string
			@param boneName: Name of the bone which we shall handle
			@type boneName: string
			@param skelStructure: The parsed skeleton structure send by the server
			@type skelStructure: dict
		"""
		readOnly = bool(skelStructure[boneName].get("readonly", False))

		if "module" in skelStructure[ boneName ].keys():
			destModule = skelStructure[ boneName ][ "module" ]
		else:
			destModule = skelStructure[ boneName ]["type"].split(".")[1]

		format = skelStructure[boneName].get("format", "$(name)")
		using = skelStructure[boneName].get("using")

		if ("params" in skelStructure[boneName].keys()
		    and skelStructure[boneName]["params"]
			and "usingDescr" in skelStructure[boneName]["params"].keys()):
			usingDescr = skelStructure[boneName]["params"]["usingDescr"]
		else:
			usingDescr = skelStructure[boneName].get("descr", boneName)

		return cls(moduleName, boneName, readOnly,
		            destModule=destModule, format=format, using=using, usingDescr = usingDescr,
		                relskel=skelStructure[boneName].get("relskel"))

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
					res["%s.%s.%s" % (self.boneName,idx,k) ] = v
			else:
				res["%s.%s.key" % (self.boneName,idx) ] = currRes
			idx += 1
		return( res )
		#return( { self.boneName: [x.data["key"] for x in self.entries]} )

	def serializeForDocument(self):
		return self.serialize()

	def onShowSelector(self, *args, **kwargs):
		"""
			Opens a ListWidget sothat the user can select new values
		"""
		currentSelector = ListWidget( self.destModule, isSelector=True )
		currentSelector.selectionActivatedEvent.register( self )
		conf["mainWindow"].stackWidget( currentSelector )
		self.parent()["class"].append("is_active")

	def onSelectionActivated(self, table, selection ):
		"""
			Merges the selection made in the ListWidget into our value(s)
		"""
		selection = [{"dest": data, "rel": getDefaultValues(self.using) if self.using else None} for data in selection]
		self.setSelection(selection)

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
			entry = RelationalMultiSelectionBoneEntry( self, self.destModule, data, self.using, errDict )
			self.addEntry( entry )

	def addEntry(self, entry):
		"""
			Adds a new RelationalMultiSelectionBoneEntry to this bone.
			@type entry: RelationalMultiSelectionBoneEntry
		"""
		assert entry not in self.entries, "Entry %s is already in relationalBone" % str(entry)
		self.entries.append(entry)
		self.selectionDiv.appendChild(entry)

	def removeEntry(self, entry ):
		"""
			Removes a RelationalMultiSelectionBoneEntry from this bone.
			@type entry: RelationalMultiSelectionBoneEntry
		"""
		assert entry in self.entries, "Cannot remove unknown entry %s from relationalBone" % str(entry)
		self.selectionDiv.removeChild( entry )
		self.entries.remove( entry )

	def moveEntry(self, entry, before = None):
		assert entry in self.entries, "Cannot remove unknown entry %s from relationalBone" % str(entry)
		self.entries.remove(entry)

		if before:
			assert before in self.entries, "Cannot remove unknown entry %s from relationalBone" % str(before)
			self.selectionDiv.insertBefore(entry, before)
			self.entries.insert(self.entries.index(before), entry)
		else:
			self.addEntry(entry)

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
	def __init__(self, extension, view, module, *args, **kwargs ):
		super( RelationalSearch, self ).__init__( *args, **kwargs )
		self.view = view
		self.extension = extension
		self.module = module
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
		currentSelector = ListWidget( self.extension["module"], isSelector=True )
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
	def canHandleExtension( extension, view, module ):
		return( isinstance( extension, dict) and "type" in extension.keys() and (extension["type"]=="relational" or extension["type"].startswith("relational.") ) )


def CheckForRelationalBoneSelection( moduleName, boneName, skelStructure, *args, **kwargs ):
	return skelStructure[boneName]["type"].startswith("relational.")

def CheckForRelationalBoneMultiSelection( moduleName, boneName, skelStructure, *args, **kwargs ):
	isMultiple = "multiple" in skelStructure[boneName].keys() and skelStructure[boneName]["multiple"]
	return isMultiple and skelStructure[boneName]["type"].startswith("relational.")

def CheckForRelationalBoneSingleSelection( moduleName, boneName, skelStructure, *args, **kwargs ):
	isMultiple = "multiple" in skelStructure[boneName].keys() and skelStructure[boneName]["multiple"]
	return not isMultiple and skelStructure[boneName]["type"].startswith("relational.")

#Register this Bone in the global queue
editBoneSelector.insert( 5, CheckForRelationalBoneMultiSelection, RelationalMultiSelectionBone)
editBoneSelector.insert( 5, CheckForRelationalBoneSingleSelection, RelationalSingleSelectionBone)
viewDelegateSelector.insert( 5, CheckForRelationalBoneSelection, RelationalViewBoneDelegate)
extendedSearchWidgetSelector.insert( 1, RelationalSearch.canHandleExtension, RelationalSearch )
extractorDelegateSelector.insert(4, CheckForRelationalBoneSelection, RelationalBoneExtractor)
