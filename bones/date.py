# -*- coding: utf-8 -*-
import datetime, logging

from vi import html5

from vi.priorityqueue import boneSelector
from vi.config import conf
from vi.bones.base import BaseBone, BaseViewWidget
from vi.i18n import translate


class DateEditWidget(html5.Div):
	style = ["vi-bone", "vi-bone--date"]

	def __init__(self, bone, **kwargs):
		super().__init__()
		self.bone = bone

		self.serverToClient = []

		if self.bone.boneStructure.get("date", True):
			self.dateInput = self.appendChild(
				"""<ignite-input type="date" />"""
			)[0]
			self.serverToClient.append("%d.%m.%Y")  # fixme: Still using German format server-side?

		else:
			self.dateInput = None

		if self.bone.boneStructure.get("time", True):
			self.timeInput = self.appendChild(
				"""<ignite-input type="time" step="1" />"""
			)[0]
			self.timeInput["readonly"] = bool(self.bone.boneStructure.get("readonly"))
			self.serverToClient.append("%H:%M:%S")
		else:
			self.timeInput = None

		assert self.dateInput or self.timeInput, "You may not configure a dateBone(date=False, time=False)"

	def unserialize(self, value=None):
		if value:
			try:
				value = datetime.datetime.strptime(value, " ".join(self.serverToClient))
			except Exception as e:
				logging.exception(e)
				value = None

			if value:
				if self.dateInput:
					self.dateInput["value"] = value.strftime("%Y-%m-%d")

				if self.timeInput:
					self.timeInput["value"] = value.strftime("%H:%M:%S")


	def serialize(self):
		value = datetime.datetime.strptime("00:00:00", "%H:%M:%S")
		haveTime = False
		haveDate = False

		if self.dateInput:
			if self.dateInput["value"]:
				try:
					date = datetime.datetime.strptime(self.dateInput["value"], "%Y-%m-%d")
					value = value.replace(year=date.year, month=date.month, day=date.day)
					haveDate = True

				except Exception as e:
					logging.exception(e)
		else:
			haveDate = True

		if self.timeInput:
			if self.timeInput["value"]:
				try:
					time = datetime.datetime.strptime(self.timeInput["value"], "%H:%M:%S")
					value = value.replace(hour=time.hour, minute=time.minute, second=time.second)
					haveTime = True

				except Exception as e:
					logging.exception(e)
			else:
				# date without time is OK!
				haveTime = haveDate and self.dateInput
		else:
			haveTime = True

		if haveDate and haveTime:
			return value.strftime(" ".join(self.serverToClient))

		return ""


class DateViewWidget(BaseViewWidget):

	def unserialize(self, value=None):
		if value:
			serverToClient = []

			if self.bone.boneStructure.get("date", True):
				serverToClient.append("%d.%m.%Y") # fixme: Again german format??

			if self.bone.boneStructure.get("time", True):
				serverToClient.append("%H:%M:%S")

			try:
				self.value = datetime.datetime.strptime(value or "", " ".join(serverToClient))
				value = self.value.strftime(translate("vi.bone.date.at").join(serverToClient)) #fixme: hmm...
			except:
				value = "Invalid Datetime Format"

		self.appendChild(html5.TextNode(value or conf["emptyValue"]), replace=True)


class DateBone(BaseBone):
	editWidgetFactory = DateEditWidget
	viewWidgetFactory = DateViewWidget

	@staticmethod
	def checkFor(moduleName, boneName, skelStructure):
		return skelStructure[boneName]["type"] == "date" or skelStructure[boneName]["type"].startswith("date.")


boneSelector.insert(1, DateBone.checkFor, DateBone)
