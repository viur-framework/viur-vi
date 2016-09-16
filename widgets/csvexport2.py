# -*- coding: utf-8 -*-
import html5, utils, datetime
from network import NetworkService, DeferredCall
from config import conf
from priorityqueue import actionDelegateSelector, extractorDelegateSelector
from i18n import translate, addTranslation

class ExportCsv(html5.Progress):
	def __init__(self, title, widget, selection, *args, **kwargs ):
		super(ExportCsv, self).__init__(*args, **kwargs)

		self.title = title
		self.widget = widget
		self.module = widget.modul
		self.params = self.widget.getFilter().copy()
		self.params["amount"] = 99
		self.data = []
		self.structure = None
		self.separator = ";"
		self.lineSeparator = "\n"
		self.encoding = "utf-8"
		self.lang = "de"

		conf["mainWindow"].log("progress", self)
		self.parent()["class"].append("is_new")
		self.parent()["class"].append("log_progress")

		DeferredCall(self.nextChunk)

	def nextChunk(self, cursor = None):
		if cursor:
			self.params["cursor"] = cursor

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

		# Visualize progress
		self["max"] = len(self.data)
		self["value"] = 0

		cellRenderer = {}
		struct = utils.boneListToDict(self.structure)
		fields = {}
		titles = []

		idx = 0
		for key, bone in self.structure:
			#if bone["visible"] and ("params" not in bone or bone["params"] is None or "ignoreForCsvExport" not in bone[
			#	"params"] or not bone["params"]["ignoreForCsvExport"]):
			if bone["visible"]:
				cellRenderer[key] = extractorDelegateSelector.select(self.module, key, struct)
				if cellRenderer[key]:
					cellRenderer[key] = cellRenderer[key](self.module, key, struct)

				fields[key] = idx
				idx += 1

				titles.append(bone.get("descr", key) or key)

		# Export
		content = self.separator.join(titles) + self.lineSeparator

		for entry in self.data:
			row = [None for _ in range(len(fields.keys()))]

			for key, value in entry.items():
				if key not in fields or value is None or str(value).lower() == "none":
					continue

				try:
					if cellRenderer[key] is not None:
						row[fields[key]] = cellRenderer[key].render(entry, key)
					else:
						row[fields[key]] = str(value)

				except ValueError:
					pass

			content += self.separator.join(row) + self.lineSeparator
			self["value"] += 1

		# Virtual File
		a = html5.A()
		a.hide()
		self.appendChild(a)

		if self.encoding == "utf-8":
			encodeURIComponent = eval("encodeURIComponent")
			a["href"] = "data:text/csv;charset=utf-8," + encodeURIComponent(content)
		elif self.encoding == "iso-8859-15":
			escape = eval("escape")
			a["href"] = "data:text/csv;charset=ISO-8859-15," + escape(content)
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
		self.parent()["class"].append("log_%s" % logClass)

		msg = html5.Span()
		html5.utils.textToHtml(msg, message)

		self.parent().appendChild(msg)
		self.parent().removeChild(self)

