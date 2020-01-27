# -*- coding: utf-8 -*-
import json

from vi import html5
from vi import utils

from vi.bones.base import BaseBoneExtractor
from vi.config import conf
from vi.framework.event import EventDispatcher
from vi.i18n import translate
from vi.priorityqueue import editBoneSelector, viewDelegateSelector, extractorDelegateSelector
from vi.widgets.internaledit import InternalEdit
from vi.framework.components.button import Button


class RecordBoneExtractor(BaseBoneExtractor):
	def __init__(self, module, boneName, skelStructure):
		super(RecordBoneExtractor, self).__init__(module, boneName, skelStructure)
		self.format = "$(dest.name)"

		if "format" in skelStructure[boneName]:
			self.format = skelStructure[boneName]["format"]

	def render(self, data, field):
		assert field == self.boneName, "render() was called with field %s, expected %s" % (field, self.boneName)

		val = data.get(field)
		if not field:
			return ""

		structure = self.skelStructure[self.boneName]

		try:
			if not isinstance(val, list):
				val = [val or ""]

			val = ", ".join([utils.formatString(self.format, x, structure["using"], language=conf["currentlanguage"])
			                 for x in val])
		except:
			# We probably received some garbage
			print("%s: RecordBoneExtractor.render cannot build relational format, maybe garbage received?" % self.boneName)
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

			val = ", ".join([utils.formatString(self.format, x, structure["using"], language=conf["currentlanguage"])
			                 for x in val])
		except:
			# We probably received some garbage
			print("%s: RecordBoneExtractor.raw cannot build relational format, maybe garbage received?" % self.boneName)
			print(val)
			return None

		return val[0] if len(val) == 1 else val


class RecordViewBoneDelegate(object):

	def __init__(self, module, boneName, structure):
		super(RecordViewBoneDelegate, self).__init__()
		self.module = module
		self.structure = structure
		self.boneName = boneName

		if "format" in structure[boneName]:
			self.format = structure[boneName]["format"]

	def render(self, data, field):
		assert field == self.boneName, "render() was called with field %s, expected %s" % (field, self.boneName)
		val = data.get(field)

		lbl = html5.Label()

		if val is None:
			lbl.appendChild(conf["empty_value"])
			return lbl

		structure = self.structure[self.boneName]

		try:
			if not isinstance(val, list):
				val = [val]
				count = 1
			else:
				count = len(val)
				if conf["maxMultiBoneEntries"] and count >= conf["maxMultiBoneEntries"]:
					val = val[:conf["maxMultiBoneEntries"] - 1]

			res = "\n".join([utils.formatString(self.format, x, structure["using"], language=conf["currentlanguage"])
			                 for x in val])

			if conf["maxMultiBoneEntries"] and count >= conf["maxMultiBoneEntries"]:
				res += "\n%s" % translate("and {count} more", count=count - conf["maxMultiBoneEntries"] - 1)

		except:
			# We probably received some garbage
			print(
					"%s: RecordViewBoneDelegate.render cannot build relational format, maybe garbage received?" % self.boneName)
			print(val)

			res = ""

		html5.utils.textToHtml(lbl, html5.utils.unescape(res))
		return lbl


class RecordSingleBone(html5.Div):
	"""
		Provides the widget for a recordBone with multiple=False
	"""

	def __init__(self, moduleName, boneName, using, readOnly, required, *args, **kwargs):
		super(RecordSingleBone, self).__init__(*args, **kwargs)

		self.addClass("recordbone", "recordbone-single")

		self.moduleName = moduleName
		self.boneName = boneName
		self.readOnly = readOnly
		self.required = required
		self.using = using

		self.mask = None

		self.changeEvent = EventDispatcher("boneChange")

		if self.readOnly:
			self["disabled"] = True

	def _setDisabled(self, disable):
		super(RecordSingleBone, self)._setDisabled(disable)
		if not disable and not self._disabledState:
			self.parent().removeClass("is_active")

	@classmethod
	def fromSkelStructure(cls, moduleName, boneName, skelStructure, *args, **kwargs):
		readOnly = skelStructure[boneName].get("readonly", False)
		required = skelStructure[boneName].get("required", False)
		using = skelStructure[boneName]["using"]

		return cls(moduleName, boneName, using, readOnly, required, )

	def unserialize(self, data):
		if self.boneName in data:
			val = data[self.boneName]
			if isinstance(val, list):
				if len(val) > 0:
					val = val[0]
				else:
					val = None

			if not isinstance(val, dict):
				val = {}

			if self.mask:
				self.removeChild(self.mask)

			self.mask = InternalEdit(self.using, val, {}, readOnly=self.readOnly, defaultCat=None)
			self.appendChild(self.mask)

	def serializeForPost(self):
		res = self.mask.serializeForPost()
		return {"%s.%s" % (self.boneName, k): v for (k, v) in res.items()}

	def serializeForDocument(self):
		return {self.boneName: self.mask.serializeForDocument()}

	@staticmethod
	def checkFor(moduleName, boneName, skelStructure, *args, **kwargs):
		isMultiple = "multiple" in skelStructure[boneName] and skelStructure[boneName]["multiple"]
		return not isMultiple and (skelStructure[boneName]["type"] == "record"
		                           or skelStructure[boneName]["type"].startswith("record."))


class RecordMultiBoneEntry(html5.Div):
	"""
		Wrapper-class that holds one referenced entry in a RecordMultiBone.
		Provides the UI to display its data and a button to remove it from the bone.
	"""

	def __init__(self, parent, module, data, using, errorInfo=None, *args, **kwargs):
		super(RecordMultiBoneEntry, self).__init__(*args, **kwargs)
		self.sinkEvent("onDrop", "onDragOver", "onDragLeave", "onDragStart", "onDragEnd", "onChange")

		self.addClass("recordbone-entry")
		self.addClass("vi-bone-container")

		self.parent = parent
		self.module = module
		self.data = data

		self.mask = InternalEdit(using, data, errorInfo, readOnly=parent.readOnly, defaultCat=None)
		self.appendChild(self.mask)

		if not parent.readOnly:
			remBtn = Button(translate("Remove"), self.onRemove, icon="icons-delete")
			remBtn.addClass("btn--remove", "btn--danger")
			self.appendChild(remBtn)

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
					self.parent.moveEntry(self.parent.currentDrag,
					                      self.parent.entries[self.parent.entries.index(self) + 1])
			else:
				self.parent.moveEntry(self.parent.currentDrag, self)

		self.parent.currentDrag = None

	def onChange(self, event):
		data = self.data.copy()
		if not isinstance(data.get("rel"), dict):
			data["rel"] = {}

		data["rel"].update(self.ie.doSave())

		self.updateLabel(data)

	def onRemove(self, *args, **kwargs):
		self.parent.removeEntry(self)
		self.parent.changeEvent.fire(self.parent)

	def serializeForPost(self):
		return self.mask.serializeForPost()

	def serializeForDocument(self):
		return self.mask.serializeForDocument()


class RecordMultiBone(html5.Div):
	"""
		Provides the widget for a recordBone with multiple=True
	"""

	def __init__(self, moduleName, boneName, readOnly, using, *args, **kwargs):
		super(RecordMultiBone, self).__init__(*args, **kwargs)

		self.addClass("recordbone", "recordbone-multi")

		self.moduleName = moduleName
		self.boneName = boneName
		self.readOnly = readOnly
		self.using = using

		self.changeEvent = EventDispatcher("boneChange")

		self.entries = []
		self.extendedErrorInformation = {}
		self.currentDrag = None
		self.currentOver = None

		if not self.readOnly:
			self.addBtn = Button( translate( "Add" ), callback = self.onAddBtnClick, icon = "icons-add" )
			self.addBtn.lang = None
			self.addBtn.addClass( "btn--add" )
			self.appendChild( self.addBtn )

		self.itemsDiv = html5.Div()
		self.itemsDiv.addClass("recordbone-entries")
		self.appendChild(self.itemsDiv)

		if self.readOnly:
			self["disabled"] = True

		self.sinkEvent("onDragOver")

	def _setDisabled(self, disable):
		"""
			Reset the is_active flag (if any)
		"""
		super(RecordMultiBone, self)._setDisabled(disable)
		if not disable and not self._disabledState:
			self.parent().removeClass("is_active")

	@classmethod
	def fromSkelStructure(cls, moduleName, boneName, skelStructure, *args, **kwargs):
		"""
			Constructs a new RecordMultiBone from the parameters given in skelStructure.
			@param moduleName: Name of the module which send us the skelStructure
			@type moduleName: string
			@param boneName: Name of the bone which we shall handle
			@type boneName: string
			@param skelStructure: The parsed skeleton structure send by the server
			@type skelStructure: dict
		"""
		readOnly = bool(skelStructure[boneName].get("readonly", False))
		using = skelStructure[boneName]["using"]

		return cls(moduleName, boneName, readOnly, using)

	def unserialize(self, data):
		"""
			Parses the values received from the server and update our value accordingly.
			@param data: The data dictionary received.
			@type data: dict
		"""
		self.itemsDiv.removeAllChildren()
		self.entries = []

		if self.boneName in data:
			val = data[self.boneName]
			if isinstance(val, dict):
				val = [val]

			self.setContent(val)

	def serializeForPost(self):
		res = {}

		for idx, entry in enumerate(self.entries):
			currRes = entry.serializeForPost()

			for k, v in currRes.items():
				res["%s.%d.%s" % (self.boneName, idx, k)] = v

		if not res:
			res[self.boneName] = None

		return res

	def serializeForDocument(self):
		return {self.boneName: [entry.serializeForDocument() for entry in self.entries]}

	def setContent(self, content):
		"""
			Set our current value to 'selection'
			@param selection: The new entry that this bone should reference
			@type selection: dict
		"""
		if content is None:
			return

		for data in content:
			errIdx = len(self.entries)
			errDict = {}

			if self.extendedErrorInformation:
				for k, v in self.extendedErrorInformation.items():
					k = k.replace("%s." % self.boneName, "")
					if 1:
						idx, errKey = k.split(".")
						idx = int(idx)
					else:
						continue

					if idx == errIdx:
						errDict[errKey] = v

			self.addEntry(RecordMultiBoneEntry(self, self.moduleName, data, self.using, errDict))

	def onAddBtnClick(self, sender=None):
		self.addEntry(RecordMultiBoneEntry(self, self.moduleName, {}, self.using))

	def addEntry(self, entry):
		"""
			Adds a new RecordMultiBoneEntry to this bone.
			@type entry: RecordMultiBoneEntry
		"""
		assert entry not in self.entries, "Entry %s is already in relationalBone" % str(entry)
		self.entries.append(entry)
		self.itemsDiv.appendChild(entry)

	def removeEntry(self, entry):
		"""
			Removes a RecordMultiBoneEntry from this bone.
			@type entry: RecordMultiBoneEntry
		"""
		assert entry in self.entries, "Cannot remove unknown entry %s from relationalBone" % str(entry)
		self.itemsDiv.removeChild(entry)
		self.entries.remove(entry)

	def moveEntry(self, entry, before=None):
		assert entry in self.entries, "Cannot remove unknown entry %s from relationalBone" % str(entry)
		self.entries.remove(entry)

		if before:
			assert before in self.entries, "Cannot remove unknown entry %s from relationalBone" % str(before)
			self.itemsDiv.insertBefore(entry, before)
			self.entries.insert(self.entries.index(before), entry)
		else:
			self.addEntry(entry)

	def setExtendedErrorInformation(self, errorInfo):
		print("------- EXTENDEND ERROR INFO --------")
		print(errorInfo)
		self.extendedErrorInformation = errorInfo
		for k, v in errorInfo.items():
			k = k.replace("%s." % self.boneName, "")
			idx, err = k.split(".")
			idx = int(idx)

			print("k: %s, v: %s" % (k, v))
			print("idx: %s" % idx)
			print(len(self.entries))
			if idx >= 0 and idx < len(self.entries):
				self.entries[idx].setError(err)
		pass

	@staticmethod
	def checkFor(moduleName, boneName, skelStructure, *args, **kwargs):
		return skelStructure[boneName].get("multiple") and (
					skelStructure[boneName]["type"] == "record"
		            	or skelStructure[boneName]["type"].startswith("record."))


def checkForRecordBone(moduleName, boneName, skelStructure, *args, **kwargs):
	return skelStructure[boneName]["type"] == "record" or skelStructure[boneName]["type"].startswith("record.")


# Register this Bone in the global queue
editBoneSelector.insert(5, RecordMultiBone.checkFor, RecordMultiBone)
editBoneSelector.insert(5, RecordSingleBone.checkFor, RecordSingleBone)
viewDelegateSelector.insert(5, checkForRecordBone, RecordViewBoneDelegate)
extractorDelegateSelector.insert(4, checkForRecordBone, RecordBoneExtractor)
