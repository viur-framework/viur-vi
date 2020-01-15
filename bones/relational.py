# -*- coding: utf-8 -*-
import json

from vi import html5
import vi.utils as utils

from vi.bones.base import BaseBoneExtractor
from vi.config import conf
from vi.framework.event import EventDispatcher
from vi.framework.components.datalist import Datalist,AutocompleteList
from vi.i18n import translate
from vi.network import NetworkService, DeferredCall
from vi.pane import Pane
from vi.priorityqueue import editBoneSelector, viewDelegateSelector, extendedSearchWidgetSelector, \
	extractorDelegateSelector

from vi.widgets.edit import EditWidget
from vi.widgets.internaledit import InternalEdit
from vi.widgets.list import ListWidget
from vi.framework.components.button import Button


def getDefaultValues(structure):
	defaultValues = {}
	for k, v in {k: v for k, v in structure}.items():
		if "params" in v.keys() and v["params"] and "defaultValue" in v["params"].keys():
			defaultValues[k] = v["params"]["defaultValue"]

	return defaultValues

class RelationalBoneExtractor(BaseBoneExtractor):
	def __init__(self, module, boneName, skelStructure):
		super(RelationalBoneExtractor, self).__init__(module, boneName, skelStructure)
		self.format = "$(dest.name)"

		if "format" in skelStructure[boneName].keys():
			self.format = skelStructure[boneName]["format"]

	def render(self, data, field ):
		assert field == self.boneName, "render() was called with field %s, expected %s" % (field, self.boneName)

		val = data.get(field)
		if not field:
			return ""

		structure = self.skelStructure[self.boneName]

		try:
			if not isinstance(val, list):
				val = [val or ""]

			val = ", ".join([(utils.formatString(
								utils.formatString(self.format, x["dest"], structure["relskel"],
								                    prefix=["dest"], language=conf["currentlanguage"]),
									x["rel"], structure["using"],
										prefix=["rel"], language=conf["currentlanguage"])
			                    or x["key"]) for x in val])
		except:
			#We probably received some garbage
			print("%s: RelationalBoneExtractor.render cannot build relational format, maybe garbage received?" % self.boneName)
			print(val)
			val = ""

		return val

	def raw(self, data, field):
		assert field == self.boneName, "render() was called with field %s, expected %s" % (field, self.boneName)

		val = data.get(field)
		if not val:
			return None

		structure = self.skelStructure[self.boneName]

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
			print("%s: RelationalBoneExtractor.raw cannot build relational format, maybe garbage received?" % self.boneName)
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
		val = data.get(field)

		delegato = html5.Div()
		delegato.addClass("vi-delegato", "vi-delegato--relational")

		if val is None:
			delegato.appendChild(conf["empty_value"])
			return delegato

		structure = self.structure[self.boneName]

		try:
			if not isinstance(val, list):
				val = [val]
				count = 1
			else:
				count = len(val)
				if conf["maxMultiBoneEntries"] and count > conf["maxMultiBoneEntries"]:
					val = val[:conf["maxMultiBoneEntries"]]

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

			if conf["maxMultiBoneEntries"] and count > conf["maxMultiBoneEntries"]:
				res += "\n%s" % translate("and {count} more", count=count - conf["maxMultiBoneEntries"])

		except:
			#We probably received some garbage
			print("%s: RelationalViewBoneDelegate.render cannot build relational format, maybe garbage received?" % self.boneName)
			print(val)

			res = ""

		html5.utils.textToHtml(delegato, html5.utils.unescape(res))
		return delegato

class RelationalMultiSelectionBoneEntry(html5.Div):
	"""
		Wrapper-class that holds one referenced entry in a RelationalMultiSelectionBone.
		Provides the UI to display its data and a button to remove it from the bone.
	"""

	def __init__(self, parent, module, data, using, errorInfo, *args, **kwargs ):
		"""
			:param parent: Reference to the RelationalMultiSelectionBone we belong to
			:type parent: RelationalMultiSelectionBone
			:param module: Name of the module which references
			:type module: str
			:param data: Values of the entry we shall display
			:type data: dict
		"""
		super(RelationalMultiSelectionBoneEntry, self).__init__(*args, **kwargs)
		self.sinkEvent("onDrop", "onDragOver", "onDragLeave", "onDragStart", "onDragEnd", "onChange")
		self.addClass("vi-bone-container")
		self.parent = parent
		self.module = module
		self.data = data

		self.txtLbl = html5.ignite.Label()
		self.txtLbl["draggable"] = not parent.readOnly

		self.addClass("vi-tree-selectioncontainer-entry")

		wrapperDiv = html5.Div()
		wrapperDiv.appendChild(self.txtLbl)
		wrapperDiv.addClass("vi-tree-labelwrapper input-group")

		# Edit button
		if (self.parent.destModule in conf["modules"].keys()
			and ("root" in conf["currentUser"]["access"]
			     or self.parent.destModule + "-edit" in conf["currentUser"]["access"])):

			self.editBtn = Button(translate("Edit"), self.onEdit, icon="icons-edit")
			self.editBtn.addClass("btn--edit")
			wrapperDiv.appendChild(self.editBtn)

		else:
			self.editBtn = None

		if not parent.readOnly:
			remBtn = Button(translate("Remove"), self.onRemove, icon="icons-delete")
			remBtn.addClass("btn--remove", "btn--danger")
			wrapperDiv.appendChild(remBtn)

		self.appendChild(wrapperDiv)

		if using:
			self.ie = InternalEdit(
				using, data["rel"], errorInfo,
			    readOnly = parent.readOnly,
			    defaultCat = parent.usingDescr
			)
			self.ie.addClass("relationwrapper")
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
			txt = utils.formatString(txt, self.ie.serializeForDocument(), self.parent.using,
			                            prefix=["rel"], language=conf["currentlanguage"])

		html5.utils.textToHtml(self.txtLbl, txt)

	def onDragStart(self, event):
		if self.parent.readOnly:
			return

		self.addClass("is-dragging")

		self.parent.currentDrag = self
		event.dataTransfer.setData("application/json", json.dumps(self.data))
		event.stopPropagation()

	def onDragOver(self, event):
		if self.parent.readOnly:
			return

		if self.parent.currentDrag is not self:
			self.addClass("is-dragging-over")
			self.parent.currentOver = self

		event.preventDefault()

	def onDragLeave(self, event):
		if self.parent.readOnly:
			return

		self.removeClass("is-dragging-over")
		self.parent.currentOver = None

		event.preventDefault()

	def onDragEnd(self, event):
		if self.parent.readOnly:
			return

		self.removeClass("is-dragging")
		self.parent.currentDrag = None

		if self.parent.currentOver:
			self.parent.currentOver.removeClass("is-dragging-over")
			self.parent.currentOver = None

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
		self.parent.changeEvent.fire(self.parent)

	def onEdit(self, sender = None):
		pane = Pane(translate("Edit"), closeable=True, iconURL="icons-edit",
					iconClasses=["module_%s" % self.parent.destModule, "apptype_list", "action_edit"])
		conf["mainWindow"].stackPane(pane, focus=True)

		try:
			edwg = EditWidget(self.parent.destModule, EditWidget.appList, key=self.data["dest"]["key"],
			                    context=self.parent.context)
			pane.addWidget(edwg)

		except AssertionError:
			conf["mainWindow"].removePane(pane)

	def serializeForPost(self):
		if self.ie:
			res = self.ie.serializeForPost()
			res["key"] = self.data["dest"]["key"]
			return res
		else:
			return {"key": self.data["dest"]["key"]}

	def serializeForDocument(self):
		res = {"rel": {}, "dest": {}}

		if self.ie:
			res["rel"] = self.ie.serializeForDocument()

		res["dest"]["key"] = self.data["dest"]["key"]
		return res

	def onAttach(self):
		super(RelationalMultiSelectionBoneEntry, self).onAttach()
		NetworkService.registerChangeListener(self)

	def onDetach(self):
		NetworkService.removeChangeListener(self)
		super(RelationalMultiSelectionBoneEntry, self).onDetach()

	def onDataChanged(self, module, key = None, **kwargs):
		if module != self.parent.destModule or key != self.data["dest"]["key"]:
			return

		self.update()

	def update(self):
		NetworkService.request(self.parent.destModule, "view",
		                        params={"key": self.data["dest"]["key"]},
		                        successHandler=self.onModuleViewAvailable)

	def onModuleViewAvailable(self, req):
		answ = NetworkService.decode(req)
		self.data["dest"] = answ["values"]
		self.updateLabel()

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
		currentSelector = ListWidget(self.extension["module"], selectMode="multi")
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

class RelationalBone(html5.Div):
	"""
		Provides the widget for a relationalBone with multiple=True
	"""

	def __init__(self, srcModule, boneName, readOnly, destModule,
	                format="$(dest.name)", using=None, usingDescr=None,
	                relskel=None, context = None, multiple=False, *args, **kwargs):
		"""
			:param srcModule: Name of the module from which is referenced
			:type srcModule: str
			:param boneName: Name of the bone thats referencing
			:type boneName: str
			:param readOnly: Prevents modifying its value if set to True
			:type readOnly: bool
			:param destModule: Name of the module which gets referenced
			:type destModule: str
			:param format: Specifies how entries should be displayed.
			:type format: str
		"""
		super(RelationalBone, self).__init__(*args, **kwargs)
		self.multiple = multiple
		self.srcModule = srcModule
		self.boneName = boneName
		self.readOnly = readOnly
		self.destModule = destModule
		self.format = format
		self.using = using
		self.usingDescr = usingDescr
		self.relskel = relskel
		self.addClass("vi-bone-container vi-tree-selectioncontainer-entry")
		self.changeEvent = EventDispatcher("boneChange")

		self.entries = []
		self.extendedErrorInformation = {}
		self.currentDrag = None
		self.currentOver = None
		self._dataprovider = None
		self.dataList = {}
		self.searchMap = {} #displayname > Key
		self.filter = {}

		self.baseContext = context
		self.context = self.baseContext.copy() if self.baseContext else None

		if (destModule.lower() in conf["modules"].keys()
			and ("root" in conf["currentUser"]["access"] or destModule + "-view" in conf["currentUser"]["access"])):

			self.quickselectionWrapper = html5.Div()
			self.quickselectionWrapper.addClass("input-group")

			self.quickselector = AutocompleteList(boneName + "_selectorid")
			self.quickselectionWrapper.appendChild(self.quickselector)

			self.addSelection = Button(translate("Add"), self.onAddSelection, icon="icons-add")
			self.addSelection.addClass("btn--add is-disabled")
			self.addSelection["disabled"] = True
			self.quickselectionWrapper.appendChild(self.addSelection)

			self.selectBtn = Button(translate("Liste"), self.onShowSelector, icon="icons-list")
			self.selectBtn.addClass("btn--select btn--primary")
			self.quickselectionWrapper.appendChild( self.selectBtn )
			self.appendChild(self.quickselectionWrapper)
		else:
			self.selectBtn = None
			self.quickselector = None
			self.addSelection = None

		self.selectionDiv = html5.Div()
		if multiple:
			self.selectionDiv.addClass("vi-relation-selectioncontainer", "vi-selectioncontainer", "list")
		self.appendChild(self.selectionDiv)
		self.selectionDiv.hide()

		if self.readOnly:
			self["disabled"] = True

		self.sinkEvent("onDragOver")

		if self.quickselector:
			DeferredCall( self.loadList, _delay = 500 )

	def selectionupdate(self):
		if self.quickselector.currentSelection:
			self.addSelection.removeClass("is-disabled")
			self.addSelection.element.disabled = False
		else:
			self.addSelection.addClass("is-disabled")
			self.addSelection["disabled"] = True

	def loadList( self ):
		self.quickselector.setDataProvider(self)

	def onNextBatchNeeded( self ):
		filter = self.filter

		if self.context:
			filter.update( self.context )

		list = NetworkService.request( self.destModule, "list", filter,
								successHandler = self.onDataAvailable,
								cacheable = True )

	def formatValue( self,entity,structure ):
		res = (utils.formatString(
					utils.formatString(
						self.format,
						entity,
						structure,
						prefix = [ "dest" ],
						language = conf[ "currentlanguage" ] ),
				entity,
				structure,
				language = conf[ "currentlanguage" ] )
			   or entity[ "key" ])

		return res

	def getFilter( self ):
		return self.filter

	def setFilter( self,filter ):
		self.quickselector.clearSuggestionList()
		self.filter = filter

	def buildPreviewList( self,list,structure ):
		for value in list:
			displayName = self.formatValue( value, structure )
			if not value[ "key" ] in self.dataList:
				self.dataList.update( { value[ "key" ]: value } )
				if displayName in self.searchMap:
					self.searchMap[displayName].append(value)
				else:
					self.searchMap.update( { displayName: [value] } )

			opt = html5.Li()
			opt[ "data" ][ "value" ] = value[ "key" ]
			opt.addClass( "item has-hover item--small" )
			opt.element.innerHTML = displayName

			self.quickselector.appendListItem( opt )

	def onDataAvailable( self, req ):
		data = NetworkService.decode( req )
		if not data or not "skellist" in data:
			return

		# Perform valuesOrder list
		if data["skellist"]:
			self.buildPreviewList(data["skellist"],data["structure"])

		elif not data["skellist"] and self.searchMap and "search" in self.filter:

			matches = [ v for k, v in self.searchMap.items() if k.startswith( self.filter["search"] ) ]
			matchlist = sum(matches,[])
			print(matches)
			print(matchlist)
			if matchlist:
				self.buildPreviewList( matchlist, data[ "structure" ] )
			else:
				self.quickselector.emptyList()
		else:
			self.quickselector.emptyList()

	def _setDisabled(self, disable):
		"""
			Reset the is-active flag (if any)
		"""
		super(RelationalBone, self)._setDisabled( disable )
		if not disable and not self._disabledState and "is-active" in self.parent()["class"]:
			self.parent().removeClass("is-active")

	@classmethod
	def fromSkelStructure(cls, moduleName, boneName, skelStructure, *args, **kwargs):
		"""
			Constructs a new RelationalMultiSelectionBone from the parameters given in skelStructure.
			:param moduleName: Name of the module which send us the skelStructure
			:type moduleName: str
			:param boneName: Name of the bone which we shall handle
			:type boneName: str
			:param skelStructure: The parsed skeleton structure send by the server
			:type skelStructure: dict
		"""
		readOnly = bool(skelStructure[boneName].get("readonly", False))

		if "module" in skelStructure[ boneName ].keys():
			destModule = skelStructure[ boneName ][ "module" ]
		else:
			destModule = skelStructure[ boneName ]["type"].split(".")[1]

		format = skelStructure[boneName].get("format", "$(name)")
		using = skelStructure[boneName].get("using")
		multiple = skelStructure[boneName].get("multiple",False)

		if ("params" in skelStructure[boneName].keys()
		    and skelStructure[boneName]["params"]
			and "usingDescr" in skelStructure[boneName]["params"].keys()):
			usingDescr = skelStructure[boneName]["params"]["usingDescr"]
		else:
			usingDescr = skelStructure[boneName].get("descr", boneName)

		if ("params" in skelStructure[boneName].keys()
		    and skelStructure[boneName]["params"]
			and "context" in skelStructure[boneName]["params"].keys()):
			context = skelStructure[boneName]["params"]["context"]
		else:
			context = None

		return cls(moduleName, boneName, readOnly,
		            destModule=destModule, format=format, using=using, usingDescr = usingDescr,
		                relskel=skelStructure[boneName].get("relskel"), context = context,multiple= multiple)

	def unserialize(self, data):
		"""
			Parses the values received from the server and update our value accordingly.
			:param data: The data dictionary received.
			:type data: dict
		"""
		if self.boneName in data.keys():
			self.selectionDiv.removeAllChildren()
			self.entries = []

			val = data[self.boneName]
			if isinstance(val, dict):
				val = [val]

			self.setSelection(val)

	def serializeForPost(self):
		"""
			Serializes our values into something that can be transferred to the server using POST.
			:returns: dict
		"""
		res = {}
		idx = 0

		for entry in self.entries:
			currRes = entry.serializeForPost()
			if isinstance( currRes, dict ):
				for k,v in currRes.items():
					res["%s.%s.%s" % (self.boneName,idx,k) ] = v
			else:
				res["%s.%s.key" % (self.boneName,idx) ] = currRes

			idx += 1

		if not res:
			res[self.boneName] = None

		return res

	def serializeForDocument(self):
		return {self.boneName: [entry.serializeForDocument() for entry in self.entries]}

	def setContext(self, context):
		self.context = self.baseContext.copy() if self.baseContext else {}

		if context:
			self.context.update(context)

	def onShowSelector(self, *args, **kwargs):
		"""
			Opens a ListWidget so that the user can select new values
		"""
		selectmode = "single"
		if self.multiple:
			selectmode = "multi"
		currentSelector = ListWidget(self.destModule, selectMode=selectmode, context=self.context)
		currentSelector.selectionActivatedEvent.register( self )
		conf["mainWindow"].stackWidget( currentSelector )
		self.parent().addClass("is-active")

	def onSelectionActivated(self, table, selection):
		"""
			Merges the selection made in the ListWidget into our value(s)
		"""
		selection = [{"dest": data, "rel": getDefaultValues(self.using) if self.using else None} for data in selection]
		self.setSelection(selection)
		self.changeEvent.fire(self)

	def onAddSelection( self, *args, **kwargs ):
		selectedOption = self.quickselector.currentSelection
		if not selectedOption:
			return 0
		selection = [ { "dest": selectedOption, "rel": getDefaultValues( self.using ) if self.using else None } ]
		self.setSelection( selection )
		self.quickselector.input["value"] = ""
		self.quickselector.currentSelection = None
		self.selectionupdate()

	def setSelection(self, selection):
		"""
			Set our current value to 'selection'
			:param selection: The new entry that this bone should reference
			:type selection: dict
		"""
		if selection is None:
			return

		for data in selection:
			errIdx = len(self.entries)
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
			self.addEntry(entry)

	def addEntry(self, entry):
		"""
			Adds a new RelationalMultiSelectionBoneEntry to this bone.
			:type entry: RelationalMultiSelectionBoneEntry
		"""
		assert entry not in self.entries, "Entry %s is already in relationalBone" % str(entry)

		if len(self.entries)==0:
			self.selectionDiv.show()

		self.entries.append(entry)
		self.selectionDiv.appendChild(entry)
		if not self.multiple:
			self.quickselectionWrapper.hide()

	def removeEntry(self, entry ):
		"""
			Removes a RelationalMultiSelectionBoneEntry from this bone.
			:type entry: RelationalMultiSelectionBoneEntry
		"""
		assert entry in self.entries, "Cannot remove unknown entry %s from relationalBone" % str(entry)
		self.selectionDiv.removeChild( entry )
		self.entries.remove( entry )
		if not self.multiple and len(self.entries)==0:
			self.quickselectionWrapper.show()
			DeferredCall(self.quickselector.updateContainer,_delay=1)
		if len(self.entries)==0:
			self.selectionDiv.hide()

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


def CheckForRelationalBoneSelection( moduleName, boneName, skelStructure, *args, **kwargs ):
	return skelStructure[boneName]["type"].startswith("relational.")

def CheckForRelationalBoneMultiSelection( moduleName, boneName, skelStructure, *args, **kwargs ):
	isMultiple = "multiple" in skelStructure[boneName].keys() and skelStructure[boneName]["multiple"]
	return isMultiple and skelStructure[boneName]["type"].startswith("relational.")

def CheckForRelationalBoneSingleSelection( moduleName, boneName, skelStructure, *args, **kwargs ):
	isMultiple = "multiple" in skelStructure[boneName].keys() and skelStructure[boneName]["multiple"]
	return not isMultiple and skelStructure[boneName]["type"].startswith("relational.")

#Register this Bone in the global queue
editBoneSelector.insert( 10, CheckForRelationalBoneMultiSelection, RelationalBone)
editBoneSelector.insert( 10, CheckForRelationalBoneSingleSelection, RelationalBone)
viewDelegateSelector.insert( 10, CheckForRelationalBoneSelection, RelationalViewBoneDelegate)
extendedSearchWidgetSelector.insert( 10, RelationalSearch.canHandleExtension, RelationalSearch )
extractorDelegateSelector.insert(10, CheckForRelationalBoneSelection, RelationalBoneExtractor)
