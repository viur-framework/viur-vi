from datetime import datetime
from html5.div import Div
from config import conf

from html5.textnode import TextNode
from html5.form import Input, Label, Select, Option
from network import NetworkService
from priorityqueue import viewDelegateSelector, actionDelegateSelector, extractorDelegateSelector
from html5.ext.button import Button
from html5.a import A
from i18n import translate

class CsvExport(Div):
	_batchSize = 99  # How many row we fetch at once

	def __init__(self, parent):
		"""
			@param parent: parent module
		"""
		super(CsvExport, self).__init__()
		self.module = parent.modul
		self._currentCursor = None
		# self._currentSearchStr = None
		self._structure = None
		self._currentRequests = []
		self.columns = []
		self.column_keys = dict()

		self.filter = parent.getFilter()
		self.columns = list()
		self.skelData = list()
		self.cell_renderer = dict()
		# Proxy some events and functions of the original table
		self.emptyNotificationDiv = Div()
		self.emptyNotificationDiv.appendChild(TextNode("Currently no entries"))
		self.emptyNotificationDiv["class"].append("emptynotification")
		self.appendChild(self.emptyNotificationDiv)

		self.emptyNotificationDiv["style"]["display"] = "none"

		if "viur.defaultlangsvalues" in conf["mainWindow"].config.keys():
			lngList = conf["mainWindow"].config["viur.defaultlangsvalues"].items()

			self.lang_select = Select()
			self.lang_select["id"] = "lang-select"

			label1 = Label(translate("Language selection"))
			label1["for"] = "lang-select"

			span1 = Div()
			span1.appendChild(label1)
			span1.appendChild(self.lang_select)
			span1["class"] = "bone"

			self.appendChild(span1)

			for key, value in lngList:
				aoption = Option()
				aoption["value"] = key
				aoption.element.innerHTML = value
				# self.appendChild(aoption)
				if key == conf["currentlanguage"]:
					aoption["selected"] = True
				self.lang_select.appendChild(aoption)
		else:
			self.lang_select = None

		# Encoding
		self.encoding_select = Select()
		self.encoding_select["id"] = "encoding-select"

		label2 = Label(translate("Encoding"))
		label2["for"] = "encoding-select"

		span2 = Div()
		span2.appendChild(label2)
		span2.appendChild(self.encoding_select)
		span2["class"] = "bone"
		self.appendChild(span2)

		tmp1 = Option()
		tmp1["value"] = "iso-8859-15"
		tmp1["selected"] = True
		tmp1.element.innerHTML = "ISO-8859-15"
		self.encoding_select.appendChild(tmp1)

		tmp2 = Option()
		tmp2["value"] = "utf-8"
		tmp2.element.innerHTML = "UTF-8"
		self.encoding_select.appendChild(tmp2)

		self.exportBtn = Button("Export", self.on_btnExport_released)
		self.appendChild(self.exportBtn)


	def onSkelStructureCompletion(self, req):
		if not req in self._currentRequests:
			return
		self._currentRequests.remove(req)
		data = NetworkService.decode(req)
		self._structure = data["structure"]
		tmpDict = {}
		for key, bone in self._structure:
			tmpDict[key] = bone

		count = 0
		for key, bone in self._structure:
			if bone["visible"]:
				self.columns.append(str(bone["descr"]))
				self.column_keys[key] = count
				count += 1
				extractor = extractorDelegateSelector.select(self.module, key, tmpDict)
				if not extractor:
					raise TypeError("missing extractor", self.module, key, tmpDict)
				extractor = extractor(self.module, key, tmpDict)
				self.cell_renderer[key] = extractor

		print("structure", self.columns)
		self.reloadData()

	def onNextBatchNeeded(self, *args, **kwargs):
		pass

	def showErrorMsg(self, req=None, code=None):
		"""
			Removes all currently visible elements and displayes an error message
		"""
		self.actionBar["style"]["display"] = "none"
		self.table["style"]["display"] = "none"
		errorDiv = Div()
		errorDiv["class"].append("error_msg")
		if code and (code == 401 or code == 403):
			txt = "Access denied!"
		else:
			txt = "An unknown error occurred!"
		errorDiv["class"].append("error_code_%s" % (code or 0))
		errorDiv.appendChild(TextNode(txt))
		self.appendChild(errorDiv)

	def DIS_onNextBatchNeeded(self):
		"""
			Requests the next rows from the server and feed them to the table.
		"""
		if self._currentCursor is not None:
			filter = self.filter.copy()
			filter["amount"] = self._batchSize
			filter["cursor"] = self._currentCursor
			self._currentRequests.append(
				NetworkService.request(self.module, "list", filter, successHandler=self.onCompletion,
					failureHandler=self.showErrorMsg))
			self._currentCursor = None

	def reloadData(self):
		"""
			Removes all currently displayed data and refetches the first batch from the server.
		"""
		self.skelData = []
		self._currentCursor = None
		self._currentRequests = []
		filter = self.filter.copy()
		filter["amount"] = self._batchSize
		self._currentRequests.append(
			NetworkService.request(self.module, "list", filter, successHandler=self.onCompletion,
			                       failureHandler=self.showErrorMsg))

	def onCompletion(self, req):
		"""
			Pass the rows received to the datatable.
			@param req: The network request that succeed.
		"""
		if not req in self._currentRequests:
			return

		self._currentRequests.remove(req)
		data = NetworkService.decode(req)

		self.emptyNotificationDiv["style"]["display"] = "none"
		skeldata = data["skellist"]
		self.skelData.extend(skeldata)
		print("cursors", self._currentCursor, data["cursor"], len(skeldata))
		if skeldata and "cursor" in data.keys():
			self._currentCursor = data["cursor"]
			self.DIS_onNextBatchNeeded()
		else:
			self._currentCursor = None
			self.dataArrived()

	def on_btnExport_released(self, *args, **kwargs):
		filter = self.filter.copy()
		filter["amount"] = 1
		self._currentRequests.append(
			NetworkService.request(self.module, "list", filter, successHandler=self.onSkelStructureCompletion,
			                       failureHandler=self.showErrorMsg))

	def dataArrived(self):
		print("exporting now...%d" % len(self.skelData))
		if not self.skelData:
			return

		current_lang = conf["currentlanguage"]
		export_lang = conf["currentlanguage"]

		if self.lang_select:
			for aoption in self.lang_select._children:
				if aoption["selected"]:
					export_lang = aoption["value"]

		encoding = "iso-8859-15"
		for aoption in self.encoding_select._children:
			if aoption["selected"]:
				encoding = aoption["value"]

		try:
			if export_lang != current_lang:
				conf["currentlanguage"] = export_lang

			data = self.skelData
			resStr = ";".join([str(i) for i in self.columns]) + "\n"
			count = len(self.columns)
			for recipient in data:
				values = [None for i in range(count)]
				for key, value in recipient.items():
					if key not in self.column_keys or value is None or value == "None" or value == "none":
						continue
					extractor = self.cell_renderer[key]
					try:
						index = self.column_keys[key]
						values[index] = extractor.render(recipient, key)
					except ValueError:
						pass
				line = ";".join(values) + "\n"
				resStr += line

			tmpA = A()
			encFunc = eval("encodeURIComponent")
			escapeFunc = eval("escape")
			if encoding == "utf-8":
				tmpA["href"] = "data:text/csv;charset=utf-8," + encFunc(resStr)
			elif encoding == "iso-8859-15":
				tmpA["href"] = "data:text/csv;charset=ISO-8859-15," + escapeFunc(resStr)
			else:
				raise ValueError("unknown encoding: %s" % encoding)
			tmpA["download"] = "export-%s-%s-%s-%s.csv" % (self.module, export_lang, encoding, datetime.now().strftime("%Y%m%d%H%M"))
			self.appendChild(tmpA)
			tmpA.element.click()
			conf["mainWindow"].removeWidget(self)
		except:
			print("ERROR OCCURED...")

		finally:
			conf["currentlanguage"] = current_lang
			# print("exporting finished")

	def onFinished(self, req):
		if self.request.isIdle():
			self.request.deleteLater()
			self.request = None
		self.overlay.inform(self.overlay.SUCCESS)

