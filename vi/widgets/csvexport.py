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
from flare.viur.bones.relational import RelationalBone
from io import BytesIO, StringIO
import csv
import js, pyodide


class ExportCsv(html5.Progress):
	def __init__(self, widget, selection, encoding = None, language = None,
	                separator = None, lineSeparator = None, expand=False, *args, **kwargs):
		super(ExportCsv, self).__init__()

		if encoding is None or encoding not in ["utf-8", "iso-8859-15"]:
			encoding = "utf-8"

		if language is None or language not in conf["server"].keys():
			language = conf["currentLanguage"]

		self.expand = expand
		self.widget = widget
		self.module = widget.module
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

		DeferredCall(self.nextChunk)

	def nextChunk(self, cursor = None):
		if cursor:
			self.params["cursor"] = cursor
		if "cursor" in self.params:
			if self.params["cursor"] is not  None and cursor is None :
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
		if answ["cursor"]:
			self.nextChunk(answ["cursor"])
		else:
			self.exportToFile()

	def exportToFile(self):
		if not self.data:
			self.replaceWithMessage(translate("No datasets to export."), logClass="info")
			return

		assert self.structure

		conf["currentLanguage"] = self.lang

		# Visualize progress
		self["max"] = len(self.data)
		self["value"] = 0

		cellRenderer = {}
		struct = {k: v for k, v in self.structure}
		fields = []
		titles = []
		outFileCSV = StringIO()
		writer = csv.writer(outFileCSV)

		subFields = {}
		for key, bone in self.structure:
			print(key, bone)

			if bone["visible"]:
				cellRenderer[key] = BoneSelector.select(self.module, key, struct)
				if cellRenderer[key]:
					cellRenderer[key] = cellRenderer[key](self.module, key, struct)

				fields.append(key)
				titles.append(bone.get("descr", key) or key)
				if self.expand and cellRenderer[key] and isinstance(cellRenderer[key], RelationalBone):
					# Check for subfields
					subFields[key] = {"dest": [], "rel": []}
					for entry in self.data:
						data = entry.get(key)
						if isinstance(data, dict):
							for subKey in (data.get("dest") or {}).keys():
								if subKey not in subFields[key]["dest"]:
									subFields[key]["dest"].append(subKey)
							for subKey in (data.get("rel") or {}).keys():
								if subKey not in subFields[key]["rel"]:
									subFields[key]["rel"].append(subKey)
					boneName = bone.get("descr", key) or key
					for subKey in subFields[key]["dest"]:
						titles.append("%s.dest.%s" % (boneName, subKey))
						fields.append("%s.dest.%s" % (key, subKey))
					for subKey in subFields[key]["rel"]:
						titles.append("%s.rel.%s" % (boneName, subKey))
						fields.append("%s.rel.%s" % (key, subKey))


		writer.writerow(titles)
		# Export
		content= self.separator.join(titles) + self.lineSeparator

		for entry in self.data:
			row = []

			for field in fields:
				#print(key, value)
				value = entry
				parts = field.split(".")
				for part in parts:
					if isinstance(value, dict):
						value = value.get(part)
					else:
						value = ""

				row.append(str(value))
			writer.writerow(row)

		outFileCSV.flush()
		outFileCSV.seek(0)
		data = outFileCSV.read().encode(self.encoding)
		filename = "export-%s-%s-%s-%s.csv" % (self.module, self.lang, self.encoding,
											   datetime.datetime.now().strftime("%Y-%m-%d"))
		blob = js.Blob.new(pyodide.to_js([data], dict_converter=js.Map.new),
						   pyodide.to_js({"type": "octet/stream"},
										 dict_converter=js.Map.new))
		url = js.window.URL.createObjectURL(blob)
		a = html5.A()
		a["href"] = url
		a["download"] = filename
		self.appendChild(a)
		a.element.click()
		js.window.URL.revokeObjectURL(url)

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

		for i, (k, v) in enumerate([("iso-8859-15", "ISO-8859-15"), ("utf-8", "UTF-8")]):
			opt = html5.Option()
			opt["value"] = k

			if i == 0:
				opt["selected"] = True

			opt.appendChild(html5.TextNode(v))
			self.encodingSelect.appendChild(opt)

		div = html5.Div()
		div.appendChild("""<input type="checkbox" [name]="expandCB" id="expandCB"><label for="expandCB">Expandieren</label>""")
		div.addClass("input-group")
		self.expandCB = div.expandCB

		self.popupBody.appendChild(div)


		self.cancelBtn = Button(translate("Cancel"), self.close, icon="icon-cancel")
		self.popupFoot.appendChild(self.cancelBtn)

		self.exportBtn = Button(translate("Export"), self.onExportBtnClick, icon="icon-download-file")
		self.exportBtn.addClass("btn--edit")
		self.popupFoot.appendChild(self.exportBtn)

	def onExportBtnClick(self, *args, **kwargs):
		encoding = self.encodingSelect["options"].item(self.encodingSelect["selectedIndex"]).value
		expand = self.expandCB.element.checked or True

		if self.langSelect:
			language = self.langSelect["options"].item(self.langSelect["selectedIndex"]).value
		else:
			language = None

		ExportCsv(self.widget, self.widget.getCurrentSelection(), encoding=encoding, language=language, expand=expand)
		self.close()
