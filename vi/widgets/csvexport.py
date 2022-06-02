# -*- coding: utf-8 -*-
import datetime
import logging
import re
from flare import html5
from flare.popup import Popup

from flare.network import NetworkService, DeferredCall
from vi.config import conf
from flare.viur import BoneSelector
from flare.i18n import translate
from flare.button import Button


class ExportCsv(html5.Progress):
	def __init__(self, widget, selection=None, encoding = None, language = None,
	                separator = None, lineSeparator = None, *args, **kwargs):
		super(ExportCsv, self).__init__()
		if encoding is None or encoding not in ["utf-8", "iso-8859-15"]:
			encoding = "utf-8"

		if language is None or language not in conf["server"].keys():
			language = conf["currentLanguage"]

		self.widget = widget
		self.module = self.widget.module
		self.selection = selection
		self.params = self.widget.getFilter().copy()
		self.params["limit"] = 99
		self.data = []
		self.structure = None
		self.separator = separator or ";"
		self.lineSeparator = lineSeparator or "\n"
		self.encoding = encoding
		self.lang = language

		conf["mainWindow"].log("progress", self, icon="icon-download-file")
		self.parent().addClass("is-new")
		self.parent().addClass("log-progress")
		self.appendChild(html5.TextNode(translate("CSV-Export")))

		DeferredCall(self.nextChunk,firstRun=True)

	def nextChunk(self, cursor = None,firstRun=False):

		if cursor is not None:
			self.params["cursor"] = cursor

		if "cursor" in self.params:
			if self.params["cursor"] is not None and cursor is None :
				self.exportToFile()
				return
		if not firstRun and cursor is None:
			self.exportToFile()
			return

		NetworkService.request(self.module, "list", self.params,
		                        successHandler=self.nextChunkComplete,
		                        failureHandler=self.nextChunkFailure)

	def nextChunkComplete(self, req):
		answ = NetworkService.decode(req)

		if self.structure is None:
			self.structure = answ["structure"]

		if not answ["skellist"]:
			self.exportToFile()
			return

		self.data.extend(answ["skellist"])
		self.nextChunk(answ["cursor"])

	def exportToFile(self):
		if not self.data:
			self.replaceWithMessage(translate("No datasets to export."), logClass="info")
			return

		assert self.structure

		defaultLanguage = conf["currentLanguage"]
		conf["currentLanguage"] = self.lang

		# Visualize progress
		self["max"] = len(self.data)
		self["value"] = 0

		cellRenderer = {}
		struct = {k: v for k, v in self.structure}
		fields = {}
		titles = []

		idx = 0
		for key, bone in self.structure:
			if key in self.selection:
				cellRenderer[key] = BoneSelector.select(self.module, key, struct)
				if cellRenderer[key]:
					cellRenderer[key] = cellRenderer[key](self.module, key, struct)

				fields[key] = idx
				idx += 1

				titles.append(bone.get("descr", key) or key)

		# Export
		content= self.separator.join(titles) + self.lineSeparator

		for entry in self.data:
			row = [str(None) for _ in range(len(fields.keys()))]

			for key, value in entry.items():

				if key not in fields or value is None or str(value).lower() == "none":
					continue

				try:
					if cellRenderer[key] is not None:
						try:
							row[fields[key]] = cellRenderer[key].toString(value)
						except:
							row[fields[key]] = str(value)
					else:
						row[fields[key]] = str(value)

				except ValueError:
					pass
			content += self.separator.join(row) + self.lineSeparator
			self["value"] += 1

		# Virtual File
		conf["currentLanguage"] = defaultLanguage

		a = html5.A()
		a.hide()
		self.appendChild(a)

		def replacer(obj):
			'''Replace an Singel Character
			to int then to to hex and the to string
			after all the last to  Character return an "%" is added

			! => to 33 => 0x21 => %21
			'''
			return "%" + str(hex(ord(obj.group(0))))[2:]


		if self.encoding == "utf-8":

			a["href"] = 'data:attachment/csv,' + html5.jseval('encodeURIComponent("%r")'%(content))
		elif self.encoding == "iso-8859-15":
			# relpace Character for and "escape"
			content = re.sub("[-_.!~*'()]", replacer,content)
			a["href"] = "data:text/csv;charset=ISO-8859-15," +html5.jseval('escape("%r")'%(content))
		else:
			raise ValueError("unknown encoding: %s" % self.encoding)

		filename = "export-%s-%s-%s-%s.csv" % (self.module, self.lang, self.encoding,
		                                       datetime.datetime.now().strftime("%Y-%m-%d"))
		a["download"] = filename
		a.element.click()

		self.replaceWithMessage(translate("{count} datasets exported\nas {filename}",
		                                    count=len(self.data), filename=filename))

		self.data = None
		self.structure = None

	def nextChunkFailure(self, req, code):
		self.replaceWithMessage(translate("Error {code} on CSV export.", code=code), logClass="error")
		self.widget.reloadData()

	def replaceWithMessage(self, message, logClass="success"):
		self.parent()["class"] = []
		self.parent().addClass("log-%s" % logClass)

		msg = html5.Span()
		html5.textToHtml(msg, message)

		self.parent().appendChild(msg)
		self.parent().removeChild(self)

class ExportCsvStarter(Popup):

	def __init__(self, widget, *args, **kwargs ):
		super(ExportCsvStarter, self).__init__(title=translate("CSV Export"))

		self.widget = widget
		self.checkboxes=[]
		if "viur.defaultlangsvalues" in conf["server"].keys():
			self.langSelect = html5.Select()
			self.langSelect.addClass("select")
			self.langSelect["id"] = "lang-select"

			lbl = html5.Label(translate("Language selection"))
			lbl.addClass("label")
			lbl["for"] = "lang-select"

			div = html5.Div()
			div.appendChild(lbl)
			div.appendChild(self.langSelect)
			div.addClass("input-group")

			self.popupBody.appendChild(div)

			for key, value in conf["server"]["viur.defaultlangsvalues"].items():
				opt = html5.Option()
				opt["value"] = key
				opt.appendChild(html5.TextNode(value))

				if key == conf["currentLanguage"]:
					opt["selected"] = True

				self.langSelect.appendChild(opt)
		else:
			self.langSelect = None

		# Encoding
		self.encodingSelect = html5.Select()
		self.encodingSelect.addClass("select")
		self.encodingSelect["id"] = "encoding-select"

		lbl = html5.Label(translate("Encoding"))
		lbl.addClass("label")
		lbl["for"] = "encoding-select"

		div = html5.Div()
		div.appendChild(lbl)
		div.appendChild(self.encodingSelect)
		div.addClass("input-group")

		self.popupBody.appendChild(div)

		for i, (k, v) in enumerate([("utf-8", "UTF-8"),("iso-8859-15", "ISO-8859-15")]):
			opt = html5.Option()
			opt["value"] = k

			if i == 0:
				opt["selected"] = True

			opt.appendChild(html5.TextNode(v))
			self.encodingSelect.appendChild(opt)
		###Select for Bones

		ul = html5.Ul()
		ul.addClass("option-group")
		self.popupBody.appendChild(ul)

		for key, bone in self.widget._structure.items():
			li = html5.Li()
			li.addClass("check")

			ul.appendChild(li)

			chkBox = html5.Input()
			chkBox.addClass("check-input")
			chkBox["type"] = "checkbox"
			chkBox["value"] = key

			li.appendChild(chkBox)
			self.checkboxes.append(chkBox)

			if key in self.widget.getFields():
				chkBox["checked"] = True
			lbl = html5.Label(bone["descr"], forElem=chkBox)
			lbl.addClass("check-label")
			li.appendChild(lbl)


		self.cancelBtn = Button(translate("Cancel"), self.close, icon="icon-cancel")
		self.popupFoot.appendChild(self.cancelBtn)

		self.exportBtn = Button(translate("Export"), self.onExportBtnClick, icon="icon-download-file")
		self.exportBtn.addClass("btn--edit")
		self.popupFoot.appendChild(self.exportBtn)

	def onExportBtnClick(self, *args, **kwargs):
		encoding = self.encodingSelect["options"].item(self.encodingSelect["selectedIndex"]).value

		if self.langSelect:
			language = self.langSelect["options"].item(self.langSelect["selectedIndex"]).value
		else:
			language = None
		selection =[]
		for checkbox  in self.checkboxes:
			if checkbox["checked"]:
				selection.append(checkbox["value"])

		ExportCsv(self.widget, encoding=encoding, language=language,selection=selection)
		self.close()


