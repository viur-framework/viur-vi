__author__ = 'stefan'

from datetime import datetime
from html5.div import Div
from pane import Pane
from event import viInitializedEvent
from config import conf

from html5.textnode import TextNode
from html5.form import Input, Label
from html5.span import Span
from widgets.table import DataTable
from network import NetworkService
from priorityqueue import viewDelegateSelector, actionDelegateSelector, extractorDelegateSelector
from html5.ext.popup import YesNoDialog
from html5.ext.button import Button
from html5.a import A

class FallbackExtractor(object):
	def __init__(self, modulName, boneName, skelStructure, *args, **kwargs ):
		super(FallbackExtractor, self ).__init__()
		self.skelStructure = skelStructure
		self.boneName = boneName
		self.modulName=modulName

	def render( self, data, field ):
		return str(data[field])


class CsvExport(Div):
	_batchSize = 99  # How many row we fetch at once

	def __init__(self, module):
		"""
			@param modul: Name of the modul we shall handle. Must be a list application!
			@type modul: string
		"""
		super(CsvExport, self).__init__()
		print("CsvExport ctor", module)
		self.module = module

		self._currentCursor = None
		# self._currentSearchStr = None
		self._structure = None
		self._currentRequests = []
		self.columns = []

		self.filter = {"state_rts": "1"}
		self.columns = list()
		self.skelData = list()
		self.cell_renderer = dict()
		# Proxy some events and functions of the original table
		self.emptyNotificationDiv = Div()
		self.emptyNotificationDiv.appendChild(TextNode("Currently no entries"))
		self.emptyNotificationDiv["class"].append("emptynotification")
		self.appendChild(self.emptyNotificationDiv)

		self.emptyNotificationDiv["style"]["display"] = "none"

		tmpList = [["de", "Deutsch"], ["en", "Englisch"]]
		tmp = Div()
		self.appendChild(tmp)
		for key, value in tmpList:
			alabel=Label()
			acheckbox=Input()
			acheckbox["type"]="checkbox"
			acheckbox["name"]=key
			if key == conf["currentlanguage"]:
				acheckbox["checked"] = True
			alabel.appendChild(acheckbox)
			aspan=Span()
			aspan.element.innerHTML=value
			alabel.appendChild(aspan)
			tmp.appendChild(alabel)

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
		for key, bone in self._structure:
			if bone["visible"]:
				self.columns.append(key)
				extractor = extractorDelegateSelector.select(self.module, key, tmpDict)
				if not extractor:
					extractor = FallbackExtractor
				extractor = extractor(self.module, key, tmpDict)
				self.cell_renderer[key] = extractor
		# print("structure", self.columns)
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
		# print("cursors", self._currentCursor, data["cursor"])
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
		print("exporting now...")
		if not self.skelData:
			return

		data = self.skelData
		idx = 1

		resStr = ";".join(self.columns) + "\n"
		count = len(self.columns)
		# print("renderers", self.cell_renderer)
		for recipient in data:
			values = [None for i in range(count)]
			for key, value in recipient.items():
				if key not in self.columns or value is None or value == "None" or value == "none":
					continue
				extractor = self.cell_renderer[key]
				try:
					index = self.columns.index(str(key))
					values[index] = extractor.render(recipient, key)
				except ValueError:
					pass
			line = ";".join(values) + "\n"
			resStr += line

		tmpA = A()
		encFunc = eval("encodeURIComponent")
		tmpA["href"] = "data:text/plain;charset=utf-8," + encFunc(resStr)
		# print("conf", conf)
		tmpA["download"] = "export-%s-%s.csv" % (self.module, datetime.now().strftime("%Y%m%d%H%M"))
		tmpA.element.click()
		# print( resStr )
		conf["mainWindow"].removeWidget(self)
		# print("exporting finished!")

	def onFinished(self, req):
		if self.request.isIdle():
			self.request.deleteLater()
			self.request = None
		self.overlay.inform(self.overlay.SUCCESS)

