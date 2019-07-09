# -*- coding: utf-8 -*-
import html5
from bones.base import BaseBoneExtractor
from widgets.button import Button
from config import conf
from event import EventDispatcher
from i18n import translate
from priorityqueue import \
	editBoneSelector,\
	viewDelegateSelector,\
	extendedSearchWidgetSelector, \
	extractorDelegateSelector


class StringBoneExtractor(BaseBoneExtractor):

	def render(self, data, field):
		if field in data.keys():
			##multilangs
			if isinstance(data[field], dict):
				resstr = ""
				if "currentlanguage" in conf.keys():
					if conf["currentlanguage"] in data[field].keys():
						resstr = data[field][conf["currentlanguage"]].replace("&quot;", "'").replace(";", " ").replace(
							'"', "'")
					else:
						if len(data[field].keys()) > 0:
							resstr = data[field][data[field].keys()[0]].replace("&quot;", "'").replace(";",
							                                                                           " ").replace('"',
							                                                                                        "'")
				return '"%s"' % resstr
			elif isinstance(data[field], list):
				return ", ".join(
					[item.replace("&quot;", "").replace(";", " ").replace('"', "'") for item in data[field]])
			elif data[field] is not None:
				return str('"%s"' % str(data[field]).replace("&quot;", "").replace(";", " ").replace('"', "'"))

		return conf["empty_value"]


class StringViewBoneDelegate(object):
	def __init__(self, moduleName, boneName, skelStructure, *args, **kwargs):
		super(StringViewBoneDelegate, self).__init__()
		self.skelStructure = skelStructure
		self.boneName = boneName
		self.moduleName = moduleName

	def render(self, data, field):
		if field not in data:
			return self.getViewElement(conf["empty_value"], False)

		value = data[field]

		##multilangs
		if isinstance(value, dict):
			if "currentlanguage" in conf and conf["currentlanguage"] in value:
				value = value[conf["currentlanguage"]]
			elif len(data[field].keys()) > 0:
				value = value[value.keys()[0]]
			else:
				value = ""

		# no langobject
		if isinstance(value, list):
			output = ", ".join(value)
		else:
			output = str(value)

		return self.getViewElement(output, False)

	def getViewElement(self, labelstr, datafield):
		labelstr = html5.utils.unescape(labelstr)
		delegato = html5.Div(labelstr)

		if datafield:
			delegato["title"] = str(datafield)

		delegato.addClass("vi-delegato", "vi-delegato--string")
		return delegato


class Tag(html5.Span):
	def __init__(self, parentBone, tag, isEditMode, readonly=False, multiLine=False, *args, **kwargs):
		super(Tag, self).__init__(*args, **kwargs)
		self.addClass("vi-bone-tag input-group")

		self.parentBone = parentBone

		if multiLine:
			self.input = html5.ignite.Textarea()
		else:
			self.input = html5.ignite.Input()
			self.input.addClass("input--small")
			self.input["type"] = "text"

		self.input["value"] = tag
		self.appendChild(self.input)

		if readonly:
			self.input["readonly"] = True
		else:
			self["draggable"] = True
			self.sinkEvent("onDrop", "onDragOver", "onDragStart", "onDragEnd")

			delBtn = Button(translate("Delete"), self.onDelBtnClick, icon="icons-delete")
			delBtn.addClass("btn--delete btn--small")
			self.appendChild(delBtn)

	def onDelBtnClick(self, *args, **kwargs):
		self.parent().removeChild(self)

	def focus(self):
		self.input.focus()

	def onDragStart(self, event):
		self.parentBone.currentTagToDrag = self
		event.dataTransfer.setData("text", self.input["value"])
		event.stopPropagation()

	def onDragOver(self, event):
		event.preventDefault()

	def onDragEnd(self, event):
		self.parentBone.currentTagToDrag = None
		event.stopPropagation()

	def onDrop(self, event):
		event.preventDefault()
		event.stopPropagation()

		tagToDrop = self.parentBone.currentTagToDrag

		if tagToDrop and tagToDrop != self:
			if self.element.offsetTop > tagToDrop.element.offsetTop:
				parentChilds = self.parent().children()

				if parentChilds[-1] is self:
					self.parent().appendChild(tagToDrop)
				else:
					self.parent().insertBefore(tagToDrop, parentChilds[parentChilds.index(self) + 1])
			else:
				self.parent().insertBefore(tagToDrop, self)

		self.parentBone.currentTagToDrag = None


class StringEditBone(html5.Div):
	def __init__(self, moduleName, boneName, readOnly, multiple=False, languages=None, multiLine=False, *args,
	             **kwargs):
		super(StringEditBone, self).__init__(*args, **kwargs)
		self.moduleName = moduleName
		self.boneName = boneName
		self.readOnly = readOnly
		self.multiple = multiple
		self.languages = languages
		self.boneName = boneName
		self.currentTagToDrag = None
		self.currentLanguage = None
		self.addClass("vi-bone-container")

		if self.languages and self.multiple:
			self.addClass("is-translated")
			self.addClass("is-multiple")
			self.languagesContainer = html5.Div()
			self.languagesContainer.addClass("vi-bone-container-langcontent")
			self.appendChild(self.languagesContainer)
			self.buttonContainer = html5.Div()
			self.buttonContainer["class"] = "vi-bone-container-langbtns input-group"
			self.appendChild( self.buttonContainer )
			self.langEdits = {}
			self.langBtns = {}

			for lang in self.languages:
				tagContainer = html5.Div()

				tagContainer.addClass("lang_%s" % lang )
				tagContainer.addClass("vi-bone-tagcontainer")
				tagContainer.hide()

				langBtn = html5.ext.Button(lang, callback=self.onLangBtnClicked)
				langBtn.addClass("btn--lang")
				langBtn.lang = lang
				self.buttonContainer.appendChild(langBtn)

				if not self.readOnly:
					addBtn = Button(translate("Add"), callback=self.onBtnGenTag, icon="icons-add")
					addBtn.addClass("btn--add")
					addBtn.lang = lang
					tagContainer.appendChild(addBtn)

				self.languagesContainer.appendChild(tagContainer)
				self.langEdits[lang] = tagContainer
				self.langBtns[lang] = langBtn

			self.setLang(self.languages[0])

		elif self.languages and not self.multiple:
			self.addClass("is-translated")
			self.languagesContainer = html5.Div()
			self.languagesContainer.addClass("vi-bone-container-langcontent")
			self.appendChild(self.languagesContainer)
			self.buttonContainer = html5.Div()
			self.buttonContainer["class"] = "vi-bone-container-langbtns input-group"
			self.appendChild( self.buttonContainer )
			self.langEdits = {}
			self.langBtns = {}

			for lang in self.languages:
				langBtn = html5.ext.Button(lang, callback=self.onLangBtnClicked)
				langBtn.addClass("btn--lang")
				langBtn.lang = lang
				self.buttonContainer.appendChild(langBtn)

				if multiLine:
					inputField = html5.ignite.Textarea()
				else:
					inputField = html5.ignite.Input()
					inputField["type"] = "text"
					inputField["placeholder"] = " "

				inputField.hide()
				inputField.addClass("lang_%s" % lang)

				if self.readOnly:
					inputField["readonly"] = True

				self.languagesContainer.appendChild(inputField)
				self.langEdits[lang] = inputField
				self.langBtns[lang] = langBtn

			self.setLang(self.languages[0])

		elif not self.languages and self.multiple:
			self.addClass("is-multiple")
			self.tagContainer = html5.Div()
			self.tagContainer.addClass("vi-bone-tagcontainer")
			self.appendChild(self.tagContainer)

			if not self.readOnly:
				addBtn = Button(translate("Add"), callback=self.onBtnGenTag, icon="icons-add")
				addBtn.lang = None
				addBtn.addClass("btn--add")

				self.tagContainer.appendChild(addBtn)

		else:  # not languages and not multiple:

			if multiLine:
				self.input = html5.ignite.Textarea()
				self.addClass("textarea")
			else:
				self.input = html5.ignite.Input()
				self.input["type"] = "text"
				self.input["placeholder"] = " "

			self.appendChild(self.input)

			if self.readOnly:
				self.input["readonly"] = True

	@staticmethod
	def fromSkelStructure(moduleName, boneName, skelStructure, *args, **kwargs):
		readOnly = "readonly" in skelStructure[boneName].keys() and skelStructure[boneName]["readonly"]

		if boneName in skelStructure.keys():
			multiple = skelStructure[boneName].get("multiple", False)
			languages = skelStructure[boneName].get("languages")
			multiLine = skelStructure[boneName].get("type") == "str.markdown"

		return StringEditBone(moduleName, boneName, readOnly, multiple=multiple, languages=languages,
		                      multiLine=multiLine)

	def onLangBtnClicked(self, btn):
		self.setLang(btn.lang)

	def isFilled(self, lang=None):
		if self.languages:
			if lang is None:
				lang = self.languages[0]

			if self.multiple:
				for item in self.langEdits[lang]._children:
					if isinstance(item, Tag) and item.input["value"]:
						return True

				return False
			else:
				return bool(len(self.langEdits[lang]["value"]))

		elif self.multiple:
			for item in self.tagContainer._children:
				if isinstance(item, Tag) and item.input["value"]:
					return True

			return False

		return bool(len(self.input["value"]))

	def _updateLanguageButtons(self):
		if not self.languages:
			return

		for lang in self.languages:
			if self.isFilled(lang):
				self.langBtns[lang].removeClass("is-unfilled")
				if not "is-filled" in self.langBtns[lang]["class"]:
					self.langBtns[lang].addClass("is-filled")
			else:
				self.langBtns[lang].removeClass("is-filled")
				if not "is-unfilled" in self.langBtns[lang]["class"]:
					self.langBtns[lang].addClass("is-unfilled")

			if lang == self.currentLanguage:
				if not "is-active" in self.langBtns[lang]["class"]:
					self.langBtns[lang].addClass("is-active")
			else:
				self.langBtns[lang].removeClass("is-active")

	def setLang(self, lang):
		if self.currentLanguage:
			self.langEdits[self.currentLanguage].hide()

		self.currentLanguage = lang
		self.langEdits[self.currentLanguage].show()
		self._updateLanguageButtons()

		for btn in self.buttonContainer._children:
			if btn.lang == lang:
				btn.addClass("is-active")
			else:
				btn.removeClass("is-active")

	def onBtnGenTag(self, btn):
		tag = self.genTag("", lang=btn.lang)
		tag.focus()

	def unserialize(self, data, extendedErrorInformation=None):
		data = data.get(self.boneName)
		if not data:
			return

		if self.languages and self.multiple:
			assert isinstance(data, dict)

			for lang in self.languages:
				for child in self.langEdits[lang].children():
					if isinstance(child, Tag):
						self.langEdits[lang].removeChild(child)

				if lang in data.keys():
					val = data[lang]

					if isinstance(val, str):
						self.genTag(html5.utils.unescape(val), lang=lang)
					elif isinstance(val, list):
						for v in val:
							self.genTag(html5.utils.unescape(v), lang=lang)

		elif self.languages and not self.multiple:
			assert isinstance(data, dict)

			for lang in self.languages:
				if lang in data.keys() and data[lang]:
					self.langEdits[lang]["value"] = html5.utils.unescape(str(data[lang]))
				else:
					self.langEdits[lang]["value"] = ""

		elif not self.languages and self.multiple:

			for child in self.tagContainer.children():
				if isinstance(child, Tag):
					self.tagContainer.removeChild(child)

			if isinstance(data, list):
				for tagStr in data:
					self.genTag(html5.utils.unescape(tagStr))
			else:
				self.genTag(html5.utils.unescape(data))

		else:
			self.input["value"] = html5.utils.unescape(str(data))

		self._updateLanguageButtons()

	def serializeForPost(self):
		res = {}

		if self.languages and self.multiple:
			for lang in self.languages:
				res["%s.%s" % (self.boneName, lang)] = []
				for child in self.langEdits[lang]._children:
					if isinstance(child, Tag):
						res["%s.%s" % (self.boneName, lang)].append(child.input["value"])

		elif self.languages and not self.multiple:
			for lang in self.languages:
				txt = self.langEdits[lang]["value"]
				if txt:
					res["%s.%s" % (self.boneName, lang)] = txt

		elif not self.languages and self.multiple:
			res[self.boneName] = []
			for child in self.tagContainer._children:
				if isinstance(child, Tag):
					res[self.boneName].append(child.input["value"])

		elif not self.languages and not self.multiple:
			res[self.boneName] = self.input["value"]

		return res

	def serializeForDocument(self):
		if self.languages and self.multiple:
			res = {}

			for lang in self.languages:
				res[lang] = []

				for child in self.langEdits[lang].children():
					if isinstance(child, Tag):
						res[lang].append(child.input["value"])

		elif self.languages and not self.multiple:
			res = {}

			for lang in self.languages:
				txt = self.langEdits[lang]["value"]

				if txt:
					res[lang] = txt

		elif not self.languages and self.multiple:
			res = []

			for child in self.tagContainer.children():
				if isinstance(child, Tag):
					res.append(child.input["value"])

		elif not self.languages and not self.multiple:
			res = self.input["value"]

		return {self.boneName: res}

	def genTag(self, tag, editMode=False, lang=None):
		tag = Tag(self, tag, editMode, readonly=self.readOnly)

		if lang is not None:
			self.langEdits[lang].appendChild(tag)
		else:
			self.tagContainer.appendChild(tag)

		return tag


def CheckForStringBone(moduleName, boneName, skelStucture, *args, **kwargs):
	return str(skelStucture[boneName]["type"]).startswith("str")


class ExtendedStringSearch(html5.Div):
	def __init__(self, extension, view, module, *args, **kwargs):
		super(ExtendedStringSearch, self).__init__(*args, **kwargs)
		self.view = view
		self.extension = extension
		self.module = module
		self.opMode = extension["mode"]
		self.filterChangedEvent = EventDispatcher("filterChanged")
		assert self.opMode in ["equals", "from", "to", "prefix", "range"]
		self.appendChild(html5.TextNode(extension["name"]))
		self.sinkEvent("onKeyDown")
		if self.opMode in ["equals", "from", "to", "prefix"]:
			self.input = html5.ignite.Input()
			self.input["type"] = "text"
			self.appendChild(self.input)
		elif self.opMode == "range":
			self.input1 = html5.ignite.Input()
			self.input1["type"] = "text"
			self.appendChild(self.input1)
			self.appendChild(html5.TextNode("to"))
			self.input2 = html5.ignite.Input()
			self.input2["type"] = "text"
			self.appendChild(self.input2)

	def onKeyDown(self, event):
		if html5.isReturn(event):
			self.filterChangedEvent.fire()

	def updateFilter(self, filter):
		if self.opMode == "equals":
			filter[self.extension["target"]] = self.input["value"]
		elif self.opMode == "from":
			filter[self.extension["target"] + "$gt"] = self.input["value"]
		elif self.opMode == "to":
			filter[self.extension["target"] + "$lt"] = self.input["value"]
		elif self.opMode == "prefix":
			filter[self.extension["target"] + "$lk"] = self.input["value"]
		elif self.opMode == "range":
			filter[self.extension["target"] + "$gt"] = self.input1["value"]
			filter[self.extension["target"] + "$lt"] = self.input2["value"]
		return (filter)

	@staticmethod
	def canHandleExtension(extension, view, module):
		return (isinstance(extension, dict) and "type" in extension.keys() and (
					extension["type"] == "string" or extension["type"].startswith("string.")))


# Register this Bone in the global queue
editBoneSelector.insert(3, CheckForStringBone, StringEditBone)
viewDelegateSelector.insert(3, CheckForStringBone, StringViewBoneDelegate)
extendedSearchWidgetSelector.insert(1, ExtendedStringSearch.canHandleExtension, ExtendedStringSearch)
extractorDelegateSelector.insert(3, CheckForStringBone, StringBoneExtractor)
