# -*- coding: utf-8 -*-
import html5
from bones.base import BaseBoneExtractor
from config import conf
from priorityqueue import editBoneSelector, viewDelegateSelector, extractorDelegateSelector
from widgets.htmleditor import HtmlEditor
from event import EventDispatcher


class TextBoneExtractor(BaseBoneExtractor):

	def render(self, data, field):
		if field in data.keys():
			##multilangs
			if isinstance(data[field], dict):
				resstr = ""
				if "currentlanguage" in conf.keys():
					if conf["currentlanguage"] in data[field].keys():
						resstr = data[field][conf["currentlanguage"]].replace("&quot;", "").replace(";", " ").replace(
							'"', "'")
					else:
						if data[field].keys().length > 0:
							resstr = data[field][data[field].keys()[0]].replace("&quot;", "").replace(";", " ").replace(
								'"', "'")
				return '"%s"' % resstr
			else:
				# no langobject
				return str('"%s"' % data[field].replace("&quot;", "").replace(";", " ").replace('"', "'"))
		return conf["empty_value"]


class TextViewBoneDelegate(object):

	def __init__(self, moduleName, boneName, skelStructure, *args, **kwargs):
		super(TextViewBoneDelegate, self).__init__()
		self.skelStructure = skelStructure
		self.boneName = boneName
		self.moduleName = moduleName

	def render(self, data, field):
		if field in data.keys():
			##multilangs
			if isinstance(data[field], dict):
				resstr = ""
				if "currentlanguage" in conf.keys():
					if conf["currentlanguage"] in data[field].keys():
						resstr = data[field][conf["currentlanguage"]]
					else:
						if data[field].keys().length > 0:
							resstr = data[field][data[field].keys()[0]]
				aspan = html5.Span()
				aspan.appendChild(html5.TextNode(resstr))
				aspan["Title"] = str(data[field])
				return (aspan)
			else:
				# no langobject
				return html5.Label(str(data[field]))
		return html5.Label(conf["empty_value"])


class TextEditBone(html5.Div):

	def __init__(self, moduleName, boneName, readOnly, isPlainText, languages=None, descrHint=None, *args, **kwargs):
		super(TextEditBone, self).__init__(*args, **kwargs)
		self.moduleName = moduleName
		self.boneName = boneName
		self.readOnly = readOnly
		self.selectedLang = False
		self.isPlainText = isPlainText
		self.languages = languages
		self.descrHint = descrHint
		self.value = {}

		# multilangbone
		if self.languages:
			if "currentlanguage" in conf and conf["currentlanguage"] in self.languages:
				self.selectedLang = conf["currentlanguage"]
			elif len(self.languages) > 0:
				self.selectedLang = self.languages[0]

			self.langButContainer = html5.Div()
			self.langButContainer["class"].append("languagebuttons")

			for lang in self.languages:
				abut = html5.ext.Button(lang, self.changeLang)
				abut["value"] = lang
				self.langButContainer.appendChild(abut)

			self.appendChild(self.langButContainer)
			self._refreshBtnStates()

		if not readOnly and not self.isPlainText:
			self.input = HtmlEditor()
			self.input.boneName = self.boneName
		else:
			self.input = html5.Textarea()
			if readOnly:
				self.input["readonly"] = True

		self.appendChild(self.input)

		self.sinkEvent("onKeyUp")

		self.changeEvent = EventDispatcher("boneChange")

	def _setDisabled(self, disable):
		"""
			Reset the is_active flag (if any)
		"""
		super(TextEditBone, self)._setDisabled(disable)
		if not disable and not self._disabledState and "is_active" in self.parent()["class"]:
			self.parent()["class"].remove("is_active")

	def changeLang(self, btn):
		self.value[self.selectedLang] = self.input["value"]
		self.selectedLang = btn["value"]
		self.input["value"] = self.value.get(self.selectedLang, "")
		self._refreshBtnStates()

	def _refreshBtnStates(self):
		for btn in self.langButContainer.children():
			if self.value.get(btn["value"]):
				btn.removeClass("is_unfilled")
				btn.addClass("is_filled")
			else:
				btn.removeClass("is_filled")
				btn.addClass("is_unfilled")

			if btn["value"] == self.selectedLang:
				btn.addClass("is_active")
			else:
				btn.removeClass("is_active")

	@staticmethod
	def fromSkelStructure(moduleName, boneName, skelStructure, *args, **kwargs):
		readOnly = "readonly" in skelStructure[boneName].keys() and skelStructure[boneName]["readonly"]
		isPlainText = "validHtml" in skelStructure[boneName].keys() and not skelStructure[boneName]["validHtml"]
		langs = skelStructure[boneName]["languages"] if (
			"languages" in skelStructure[boneName].keys() and skelStructure[boneName]["languages"]) else None
		descr = skelStructure[boneName]["descr"] if "descr" in skelStructure[boneName].keys() else None
		return TextEditBone(moduleName, boneName, readOnly, isPlainText, langs, descrHint=descr)

	def unserialize(self, data):
		data = data.get(self.boneName) or ""

		if self.languages:
			self.value.clear()

			for lang in self.languages:
				if isinstance(data, dict):
					self.value[lang] = data.get(lang, "")
				else:
					self.value[lang] = data

			self.input["value"] = self.value[self.selectedLang]
			self._refreshBtnStates()
		else:
			self.input["value"] = data

	def serializeForPost(self):
		if self.selectedLang:
			self.value[self.selectedLang] = self.input["value"]
			return {self.boneName: self.value.copy()}

		return {self.boneName: self.input["value"]}

	def serializeForDocument(self):
		return self.serializeForPost()

	def setExtendedErrorInformation(self, errorInfo):
		pass

	def onKeyUp(self, event):
		self.changeEvent.fire(self)

	@staticmethod
	def checkForTextBone(moduleName, boneName, skelStucture, *args, **kwargs):
		return skelStucture[boneName]["type"] == "text"


# Register this Bone in the global queue
editBoneSelector.insert(3, TextEditBone.checkForTextBone, TextEditBone)
viewDelegateSelector.insert(3, TextEditBone.checkForTextBone, TextViewBoneDelegate)
extractorDelegateSelector.insert(3, TextEditBone.checkForTextBone, TextBoneExtractor)
