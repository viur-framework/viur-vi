# -*- coding: utf-8 -*-
import html5
from priorityqueue import editBoneSelector, viewDelegateSelector, extractorDelegateSelector, extendedSearchWidgetSelector
from datetime import datetime
import re
from event import EventDispatcher
from i18n import translate
from config import conf
from bones.base import BaseBoneExtractor


class DateBoneExtractor(BaseBoneExtractor):

	def render(self, data, field):
		if not(self.boneName in self.skelStructure
		        and data and data.get(field)):
			return conf["empty_value"]

		structure = self.skelStructure[self.boneName]
		val = data[field]

		try:
			if structure["date"] and structure["time"]:
				try:
					dt = datetime.strptime( val, "%d.%m.%Y %H:%M:%S")
				except:
					return "Error parsing Date"

				return dt.strftime("%d.%m.%Y %H:%M:%S")

			elif structure["date"] and not structure["time"]:
				try:
					dt = datetime.strptime( val, "%d.%m.%Y")
				except:
					return "Error parsing Date"

				return dt.strftime("%d.%m.%Y")

			elif not structure["date"] and structure["time"]:
				try:
					dt = datetime.strptime( val, "%H:%M:%S")
				except:
					return "Error parsing time"

				return dt.strftime("%H:%M:%S")

		except:
			return str(val)


class DateViewBoneDelegate( object ):
	def __init__(self, moduleName, boneName, skelStructure, *args, **kwargs ):
		super( DateViewBoneDelegate, self ).__init__()
		self.skelStructure = skelStructure
		self.boneName = boneName
		self.moduleName = moduleName

	def render( self, data, field ):

		if not(self.boneName in self.skelStructure and data and data.get(field)):
			return html5.Label(conf["empty_value"])

		structure = self.skelStructure[self.boneName]
		val = data[field]

		try:
			if structure["date"] and structure["time"]:
				try:
					dt = datetime.strptime(val, "%d.%m.%Y %H:%M:%S")
				except:
					return html5.TextNode(translate("Error parsing Date"))

				span = html5.Span()
				span["class"].append("datetime")
				dateSpan = html5.Span()
				dateSpan["class"].append("date")
				dateSpan.appendChild( html5.TextNode( dt.strftime("%d.%m.%Y") ))
				timeSpan = html5.Span()
				timeSpan["class"].append("time")
				timeSpan.appendChild( html5.TextNode( dt.strftime("%H:%M:%S") ))
				span.appendChild(dateSpan)
				span.appendChild(timeSpan)

				return span

			elif structure["date"] and not structure["time"]:
				try:
					dt = datetime.strptime( val, "%d.%m.%Y")
				except:
					return html5.TextNode(translate("Error parsing Date"))

				dateSpan = html5.Span()
				dateSpan["class"].append("date")
				dateSpan.appendChild(html5.TextNode(dt.strftime("%d.%m.%Y")))

				return dateSpan

			elif not structure["date"] and structure["time"]:
				try:
					dt = datetime.strptime(val, "%H:%M:%S")
				except:
					return html5.TextNode(translate("Error parsing Date"))

				timeSpan = html5.Span()
				timeSpan["class"].append("time")
				timeSpan.appendChild( html5.TextNode(dt.strftime("%H:%M:%S")))
				return timeSpan

		except: #Something got wrong parsing the date
			return html5.Label(str(val))


class DateEditBone( html5.Div ):
	def __init__(self, moduleName, boneName, readOnly, date=True, time=True, *args, **kwargs ):
		super( DateEditBone,  self ).__init__(*args, **kwargs)
		self.boneName = boneName
		self.readOnly = readOnly
		self.hasdate = date
		self.hastime = time

		if date:
			self.dateinput = html5.Input()

			#IE11
			try:
				self.dateinput["type"] = "date"
			except:
				pass

			self.dateinput["style"]["float"] = "left"
			self.appendChild(self.dateinput)

			if self.readOnly:
				self.dateinput["readonly"] = True

		if time:
			self.timeinput=html5.Input()

			#IE11
			try:
				self.timeinput["type"] = "time"
			except:
				pass

			self.timeinput["style"]["float"] = "left"   #fixme: Do this with css?
			self.timeinput["style"]["width"] = "70px"   #fixme: Do this with css?
			self.appendChild(self.timeinput)

			if self.readOnly:
				self.timeinput["readonly"] = True

	@staticmethod
	def fromSkelStructure(moduleName, boneName, skelStructure, *args, **kwargs):
		readOnly = "readonly" in skelStructure[ boneName ].keys() and skelStructure[ boneName ]["readonly"]
		date = skelStructure[ boneName ]["date"] if "date" in skelStructure[ boneName ].keys() else True
		time = skelStructure[ boneName ]["time"] if "time" in skelStructure[ boneName ].keys() else True
		return DateEditBone(moduleName, boneName, readOnly, date, time)

	def unserialize(self, data, extendedErrorInformation=None):
		if data.get(self.boneName):
			if self.hastime and not self.hasdate:
				self.timeinput["value"] = data[ self.boneName ]

			if self.hasdate and not self.hastime:
				dateobj = datetime.strptime(data[ self.boneName ], "%d.%m.%Y")
				self.dateinput["value"] = dateobj.strftime( "%Y-%m-%d" )

			if self.hasdate and self.hastime:
				# FIXME: temporarily fixing a bug in extended relational bone
				try:
					dateobj = datetime.strptime(data[self.boneName], "%d.%m.%Y %H:%M:%S")
					self.dateinput["value"]=dateobj.strftime("%Y-%m-%d")
					self.timeinput["value"]=dateobj.strftime("%H:%M:%S")

				except ValueError:
					self.dateinput["value"] = "-"
					self.timeinput["value"] = "-"

	def serializeForPost(self):
		#[day, month, year, hour, min, sec]
		adatetime=["00","00","0000","00","00","00"]

		if hasattr(self,"timeinput"):
			result = re.match('(\d+):(\d+)(:(\d+))?',self.timeinput["value"])
			if result:
				adatetime[3] = result.group(1)
				adatetime[4] = result.group(2)

				if result.group(4):
					adatetime[5] = result.group(4)

		if hasattr(self,"dateinput"):
			result = re.match('(\d+).(\d+).(\d+)',self.dateinput["value"])
			if result:
				adatetime[0] = result.group(3)
				adatetime[1] = result.group(2)
				adatetime[2] = result.group(1)

		if adatetime[2]=="0000":
			return {self.boneName: adatetime[3]+":"+adatetime[4]+":00"}

		returnvalue = adatetime[0]+"."+adatetime[1]+"."+adatetime[2]+" "+adatetime[3]+":"+adatetime[4]+":"+adatetime[5]
		return {self.boneName: returnvalue}

	def serializeForDocument(self):
		return self.serializeForPost()


def CheckForDateBone(moduleName, boneName, skelStucture, *args, **kwargs):
	return skelStucture[boneName]["type"] == "date"


class DateRangeFilterPlugin(html5.Div):
	def __init__(self, extension, view, modul, *args, **kwargs):
		super(DateRangeFilterPlugin, self).__init__(*args, **kwargs)
		self.view = view
		self.extension = extension
		self.modul = modul
		self.mutualExclusiveGroupTarget = "daterange-filter"
		self.mutualExclusiveGroupKey = extension["target"]
		self.filterChangedEvent = EventDispatcher("filterChanged")
		title = html5.H2()
		title.appendChild(html5.TextNode(extension["name"]))
		self.appendChild(title)

		# from daterange value
		self.fromDatepicker = html5.Input()
		self.fromDatepicker["type"] = "date"
		self.fromDatepicker["id"] = "from-date-%s" % self.extension["target"]
		self.fromDatepicker["class"] = "extended-date-range-filter"
		fromLabel = html5.Label("Startdatum")
		fromLabel["for"] = "from-date"
		span = html5.Span()
		span.appendChild(fromLabel)
		span.appendChild(self.fromDatepicker)
		self.appendChild(span)

		# to daterange value
		self.toDatepicker = html5.Input()
		self.toDatepicker["type"] = "date"
		self.toDatepicker["id"] = "to-date-%s" % self.extension["target"]
		self.toDatepicker["class"] = "extended-date-range-filter %s" % self.extension["target"]
		toLabel = html5.Label("Enddatum")
		toLabel["for"] = "to-date"
		span2 = html5.Span()
		span2.appendChild(toLabel)
		span2.appendChild(self.toDatepicker)
		self.appendChild(span2)
		self.clearButton = html5.ext.Button("Filter entfernen", self.clearFilter)
		self.appendChild(self.clearButton)
		self.sinkEvent("onChange")

	def clearFilter(self, fire=True):
		self.fromDatepicker["value"] = None
		self.toDatepicker["value"] = None
		if fire:
			self.filterChangedEvent.fire()

	def updateFilter(self, filter, mutualExclusiveGroupTarget=None, mutualExclusiveGroupKey=None):
		print("updateFilter", self.extension["target"], filter, mutualExclusiveGroupTarget)
		if mutualExclusiveGroupTarget == self.mutualExclusiveGroupTarget and mutualExclusiveGroupKey != self.mutualExclusiveGroupKey:
			del filter["%s$gt" % self.extension["target"]]
			del filter["%s$lt" % self.extension["target"]]
			self.clearFilter(False)
			return filter

		clearedFilter = {}
		for key, value in filter.items():
			if key.find("$") != -1 and key.find(self.extension["target"]) == -1:
				continue
			else:
				clearedFilter[key] = value
		print("clearedFilter before new values", self.extension["target"], clearedFilter)
		if self.fromDatepicker["value"] and self.toDatepicker["value"]:
			clearedFilter["orderby"] = self.extension["target"]
			clearedFilter["%s$gt" % self.extension["target"]] = self.fromDatepicker["value"]
			clearedFilter["%s$lt" % self.extension["target"]] = self.toDatepicker["value"]
		print("clearedFilter result", self.extension["target"], clearedFilter)
		return clearedFilter

	def onChange(self, event):
		event.stopPropagation()
		self.filterChangedEvent.fire(
			mutualExclusiveGroupTarget=self.mutualExclusiveGroupTarget,
			mutualExclusiveGroupKey=self.mutualExclusiveGroupKey
		)

	@staticmethod
	def canHandleExtension(extension, view, modul):
		print("canHandleExtension", extension, view, modul)
		return isinstance(extension, dict) and "type" in extension.keys() and (extension["type"] == "date" or extension["type"].startswith("date."))


# Register this Bone in the global queue
editBoneSelector.insert(3, CheckForDateBone, DateEditBone)
viewDelegateSelector.insert(3, CheckForDateBone, DateViewBoneDelegate)
extractorDelegateSelector.insert(3, CheckForDateBone, DateBoneExtractor)
extendedSearchWidgetSelector.insert(1, DateRangeFilterPlugin.canHandleExtension, DateRangeFilterPlugin)
