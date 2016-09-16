# -*- coding: utf-8 -*-
import html5, utils, datetime
from network import NetworkService, DeferredCall
from config import conf
from priorityqueue import actionDelegateSelector, extractorDelegateSelector
from i18n import translate, addTranslation

class ExportCsv(html5.Progress):
	def __init__(self, title, widget, selection, *args, **kwargs ):
		super(ExportCsv, self).__init__( *args, **kwargs )

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
		assert self.structure

		# Visualize progress
		self["max"] = len(self.data)
		self["value"] = 0

		cellRenderer = {}
		struct = utils.boneListToDict(self.structure)
		fields = {}
		titles = []

		for idx, (key, bone) in enumerate(self.structure):
			#if bone["visible"] and ("params" not in bone or bone["params"] is None or "ignoreForCsvExport" not in bone[
			#	"params"] or not bone["params"]["ignoreForCsvExport"]):
			if bone["visible"]:
				cellRenderer[key] = extractorDelegateSelector.select(self.module, key, struct)
				if not cellRenderer[key]:
					raise TypeError("Missing extractor", self.module, key, struct)

				cellRenderer[key] = cellRenderer[key](self.module, key, struct)

				fields[key] = idx
				titles.append(bone.get("descr", key) or key)

		# Export
		content = self.separator.join(titles) + self.lineSeparator

		for entry in self.data:
			row = [None for i in range(len(self.data))]

			for key, value in entry.items():
				if key not in fields or value is None or str(value).lower() == "none":
					continue

				try:
					print(cellRenderer[key])
					row[fields[key]] = cellRenderer[key].render(entry, key)
				except ValueError:
					pass

			content += self.separator.join(row) + self.lineSeparator + "\n"
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

		self.replaceWithMessage(translate("{count} datasets exported as {filename}",
		                                    count=len(self.data), filename=filename),
		                        isSuccess=True)

		self.data = None
		self.structure = None

	def nextChunkFailure(self, req, code):
		self.replaceWithMessage(translate("Error {code} on CSV export.", code=code), isSuccess=False)
		self.widget.reloadData()

	def replaceWithMessage(self, message, isSuccess):
		self.parent()["class"] = []

		if isSuccess:
			self.parent()["class"].append("log_success")
		else:
			self.parent()["class"].append("log_failed")

		msg = html5.Span()
		msg.appendChild(html5.TextNode(message))
		self.parent().appendChild(msg)
		self.parent().removeChild(self)

