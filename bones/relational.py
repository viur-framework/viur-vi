# -*- coding: utf-8 -*-
import json

from vi import html5
import vi.utils as utils

from vi.bones.base import BaseBoneExtractor
from vi.config import conf
from vi.framework.event import EventDispatcher
from vi.i18n import translate
from vi.network import NetworkService
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


class RelationalSingleSelectionBone(html5.Div):
	"""
		Provides the widget for a relationalBone with multiple=False
	"""

	def __init__(self, srcModule, boneName, readOnly, destModule, format="$(dest.name)", required=False,
	                using = None, usingDescr = None, context = None, *args, **kwargs ):
		"""
			:param srcModule: Name of the module from which is referenced
			:type srcModule: string
			:param boneName: Name of the bone thats referencing
			:type boneName: str
			:param readOnly: Prevents modifying its value if set to True
			:type readOnly: bool
			:param destModule: Name of the module which gets referenced
			:type destModule: str
			:param format: Specifies how entries should be displayed.
			:type format: str
		"""
		super(RelationalSingleSelectionBone,  self).__init__(*args, **kwargs)
		self.srcModule = srcModule
		self.boneName = boneName
		self.readOnly = readOnly
		self.destModule = destModule
		self.format = format
		self.using = using
		self.usingDescr = usingDescr
		self.addClass("vi-bone-container")
		self.addClass("vi-tree-selectioncontainer-entry")

		self.selection = None
		self.selectionTxt = html5.ignite.Input()
		self.selectionTxt["readonly"] = True
		self.selectionTxt["type"] = "text"

		self.ie = None

		self.boneControls = html5.Div()
		self.boneControls.addClass("vi-bone-controls input-group")

		wrapperDiv = html5.Div()
		wrapperDiv.addClass( "vi-tree-labelwrapper input-group" )

		wrapperDiv.appendChild( self.selectionTxt )
		wrapperDiv.appendChild( self.boneControls )

		self.appendChild(wrapperDiv)
		self.baseContext = context
		self.context = self.baseContext.copy() if self.baseContext else None

		self.changeEvent = EventDispatcher("boneChange")

		# Selection button
		if (destModule in conf["modules"].keys()
			and ("root" in conf["currentUser"]["access"] or destModule + "-view" in conf["currentUser"]["access"])):

			self.selectBtn = html5.ext.Button(translate("Select"), self.onShowSelector)
			self.selectBtn.addClass("btn--select")
			self.boneControls.appendChild(self.selectBtn)
		else:
			self.selectBtn = None

		# Edit button
		if (destModule in conf["modules"].keys()
			and ("root" in conf["currentUser"]["access"] or destModule + "-edit" in conf["currentUser"]["access"])):
			self.editBtn = html5.ext.Button(translate("Edit"), self.onEdit )
			self.editBtn.addClass("btn--edit")
			self.boneControls.appendChild(self.editBtn)
		else:
			self.editBtn = None

		# Remove button
		if (not required and not readOnly
		    and ("root" in conf["currentUser"]["access"]
		            or destModule + "-view" in conf["currentUser"]["access"])):
			# Yes, we check for "view" on the remove button, because removal of relations
			# is only useful when viewing the destination module is still allowed.

			self.remBtn = html5.ext.Button(translate("Remove"), self.onRemove )
			self.remBtn.addClass("btn--remove", "btn--danger")
			self.boneControls.appendChild(self.remBtn)
		else:
			self.remBtn = None

		if self.readOnly:
			self["disabled"] = True

	def _setDisabled(self, disable):
		"""
			Reset the is-active flag (if any)
		"""
		super(RelationalSingleSelectionBone, self)._setDisabled( disable )
		if not disable and not self._disabledState and "is-active" in self.parent()["class"]:
			self.parent().removeClass("is-active")

	@classmethod
	def fromSkelStructure(cls, moduleName, boneName, skelStructure, *args, **kwargs):
		"""
			Constructs a new RelationalSingleSelectionBone from the parameters given in skelStructure.
			:param moduleName: Name of the module which send us the skelStructure
			:type moduleName: str
			:param boneName: Name of the bone which we shall handle
			:type boneName: str
			:param skelStructure: The parsed skeleton structure send by the server
			:type skelStructure: dict
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

		if ("params" in skelStructure[boneName].keys()
		    and skelStructure[boneName]["params"]
			and "context" in skelStructure[boneName]["params"].keys()):
			context = skelStructure[boneName]["params"]["context"]
		else:
			context = None

		return cls(moduleName, boneName, readOnly, destModule=destModule,
		            format=format, required=required, using=using, usingDescr=usingDescr,
		            context = context)

	def setContext(self, context):
		self.context = {}

		if context:
			self.context.update(context)

		if self.baseContext:
			self.context.update(self.baseContext)

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
			edwg = EditWidget(self.destModule, EditWidget.appList,
			                    key=self.selection["dest"]["key"],
			                    context=self.context)
			pane.addWidget(edwg)

		except AssertionError:
			conf["mainWindow"].removePane(pane)

	def onRemove(self, *args, **kwargs):
		self.setSelection(None)
		self.changeEvent.fire(self)
		if self.ie:
			self.removeChild( self.ie )


	def unserialize(self, data):
		"""
			Parses the values received from the server and update our value accordingly.
			:param data: The data dictionary received.
			:type data: dict
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

					self.ie = InternalEdit(
						self.using, val["rel"], {},
					    readOnly=self.readOnly,
					    defaultCat=self.usingDescr
					)
					self.ie.addClass("relationwrapper")
					self.appendChild(self.ie)
			else:
				self.setSelection(None)

	def serializeForPost(self):
		"""
			Serializes our value into something that can be transferred to the server using POST.
			:returns: dict
		"""
		res = {}

		if not (self.selection and "dest" in self.selection.keys() and "key" in self.selection["dest"].keys()):
			return res

		if self.ie:
			res.update(self.ie.serializeForPost())

		res["key"] = self.selection["dest"]["key"]

		return {"%s.0.%s" % (self.boneName, k): v for (k,v ) in res.items()}

	def serializeForDocument(self):
		res = {"rel": {}, "dest": {}}

		if (self.selection and "dest" in self.selection.keys()):
			if self.ie:
				res["rel"].update(self.ie.serializeForDocument())

			res["dest"] = self.selection["dest"]

		return {self.boneName: res}

	def onShowSelector(self, *args, **kwargs):
		"""
			Opens a ListWidget so that the user can select new values
		"""

		try:
			currentSelector = ListWidget(self.destModule, selectMode="single", context=self.context)
		except AssertionError:
			return

		currentSelector.selectionActivatedEvent.register( self )
		conf["mainWindow"].stackWidget( currentSelector )
		self.parent().addClass("is-active")

	def onSelectionActivated(self, table, selection ):
		"""
			Merges the selection made in the ListWidget into our value(s)
		"""
		if selection:
			self.setSelection({"dest": selection[0]})
		else:
			self.setSelection(None)

		self.changeEvent.fire(self)

	def setSelection(self, selection):
		"""
			Set our current value to 'selection'
			:param selection: The new entry that this bone should reference
			:type selection: dict
		"""
		if not selection:
			selection = {}
			self.selection = None

		if not self.selection:
			self.selection = {}

		self.selection.update(selection)

		if selection:
			NetworkService.request(self.destModule, "view/%s" % selection["dest"]["key"],
			                        self.context or {},
			                        successHandler=self.onSelectionDataAvailable, cacheable=True)

			self.selectionTxt["value"] = translate("Loading...")

			if self.using and not self.ie:
				self.ie = InternalEdit(
					self.using, getDefaultValues(self.using), {},
				    readOnly=self.readOnly,
					defaultCat=self.usingDescr
				)
				self.ie.addClass("relationwrapper")

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
				self.editBtn.enable()
			if self.remBtn:
				self.remBtn.enable()
		else:
			if self.editBtn:
				self.editBtn.disable()
			if self.remBtn:
				self.remBtn.disable()

	def onAttach(self):
		super(RelationalSingleSelectionBone, self).onAttach()
		NetworkService.registerChangeListener(self)

	def onDetach(self):
		NetworkService.removeChangeListener(self)
		super(RelationalSingleSelectionBone, self).onDetach()

	def onDataChanged(self, module, key = None, **kwargs):
		if module == self.destModule and self.selection and key == self.selection["dest"]["key"]:
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

		# Edit button
		if (self.parent.destModule in conf["modules"].keys()
			and ("root" in conf["currentUser"]["access"]
					or self.parent.destModule + "-edit" in conf["currentUser"]["access"])):

			self.editBtn = Button(translate("Edit"), self.onEdit, icon="icons-edit")
			self.editBtn.addClass("btn--edit")
			wrapperDiv.appendChild(self.editBtn)

		else:
			self.editBtn = None


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

class RelationalMultiSelectionBone(html5.Div):
	"""
		Provides the widget for a relationalBone with multiple=True
	"""

	def __init__(self, srcModule, boneName, readOnly, destModule,
	                format="$(dest.name)", using=None, usingDescr=None,
	                relskel=None, context = None, *args, **kwargs):
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
		super(RelationalMultiSelectionBone, self).__init__(*args, **kwargs)

		self.srcModule = srcModule
		self.boneName = boneName
		self.readOnly = readOnly
		self.destModule = destModule
		self.format = format
		self.using = using
		self.usingDescr = usingDescr
		self.relskel = relskel
		self.addClass("vi-bone-container")

		self.changeEvent = EventDispatcher("boneChange")

		self.entries = []
		self.extendedErrorInformation = {}
		self.currentDrag = None
		self.currentOver = None

		self.baseContext = context
		self.context = self.baseContext.copy() if self.baseContext else None

		self.selectionDiv = html5.Div()
		self.selectionDiv.addClass("vi-relation-selectioncontainer", "vi-selectioncontainer", "list")
		self.appendChild(self.selectionDiv)

		print(conf["modules"].keys())
		if (destModule.lower() in conf["modules"].keys()
			and ("root" in conf["currentUser"]["access"] or destModule + "-view" in conf["currentUser"]["access"])):

			self.selectBtn = html5.ext.Button(translate("Select"), self.onShowSelector)
			self.selectBtn.addClass("btn--select")
			self.appendChild( self.selectBtn )
		else:
			self.selectBtn = None

		if self.readOnly:
			self["disabled"] = True

		self.sinkEvent("onDragOver")

	def _setDisabled(self, disable):
		"""
			Reset the is-active flag (if any)
		"""
		super(RelationalMultiSelectionBone, self)._setDisabled( disable )
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
		                relskel=skelStructure[boneName].get("relskel"), context = context)

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
		currentSelector = ListWidget(self.destModule, selectMode="multi", context=self.context)
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
		self.entries.append(entry)
		self.selectionDiv.appendChild(entry)

	def removeEntry(self, entry ):
		"""
			Removes a RelationalMultiSelectionBoneEntry from this bone.
			:type entry: RelationalMultiSelectionBoneEntry
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
