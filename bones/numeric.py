# -*- coding: utf-8 -*-
import re, logging
from vi import html5

from vi.priorityqueue import boneSelector
from vi.config import conf
from vi.bones.base import BaseBone, BaseViewWidget


class NumericEditWidget(html5.Div):
	style = ["vi-bone", "vi-bone--numeric"]

	def __init__(self, bone, **kwargs):
		super().__init__()

		# Bone references
		self.bone = bone
		self.value = None

		# Numeric bone precision, min and max
		self.precision = self.bone.boneStructure.get("precision") or 0
		self.min = html5.utils.parseFloat(str(self.bone.boneStructure.get("min")), None)
		self.max = html5.utils.parseFloat(str(self.bone.boneStructure.get("max")), None)

		# Currency mode
		self.currency = None
		self.currencyDecimalDelimiter = ","
		self.currencyThousandDelimiter = "."
		self.currencyPattern = None

		# Style parameters
		style = (self.bone.boneStructure.get("params") or {}).get("style", "")
		for s in style.split(" "):
			if s.lower().startswith("amount."):
				self.currency = s.split(".", 1)[1]
				if self.bone.boneStructure.get("precision") is None:
					self.precision = 2  #default precision for amounts

			if s.lower().startswith("delimiter."):
				fmt = s.split(".", 1)[1]
				if fmt == "dot":
					self.currencyDecimalDelimiter = "."
					self.currencyThousandDelimiter = ","
				# else: fixme are there more configs?

		self.widget = self._createWidget()

	def _createWidget(self):
		self.sinkEvent("onChange")
		return self.appendChild(html5.ignite.Input())[0]

	def _configureWidget(self):
		# Widget state
		self.widget["readonly"] = bool(self.bone.boneStructure.get("readonly"))
		self.widget["required"] = bool(self.bone.boneStructure.get("required"))

		# Standard- or currency mode
		if not self.currency:
			self.widget["type"] = "number"

			if self.precision:
				self.widget["step"] = pow(10, -self.precision)

			else:  # Precision is zero, treat as integer input
				self.widget["step"] = 1

			if self.min is not None:
				self.widget["min"] = self.min

			if self.max is not None:
				self.widget["max"] = self.max

		else:
			assert self.currencyThousandDelimiter[0] not in "^-+()[]"
			assert self.currencyDecimalDelimiter[0] not in "^-+()[]"

			self.currencyPattern = re.compile(r"-?((\d{1,3}[%s])*|\d*)[%s]\d+|-?\d+" %
			                                    (self.currencyThousandDelimiter[0],
			                                        self.currencyDecimalDelimiter[0]))

	def setValue(self, value):
		if not self.currency:
			if self.precision:
				self.value = html5.utils.parseFloat(value or 0)
			else:
				self.value = html5.utils.parseInt(value or 0)

			return str(self.value)

		if value is None or str(value).strip() is "":
			self.value = None
			return ""

		if isinstance(value, float):
			value = str(value).replace(".", self.currencyDecimalDelimiter)

		value = str(value).strip()

		if self.currencyPattern.match(value):
			try:
				value = re.sub(r"[^-0-9%s]" % self.currencyDecimalDelimiter, "", value)
				value = value.replace(self.currencyDecimalDelimiter, ".")

				if self.precision == 0:
					self.value = int(float(value))
					value = [str(self.value)]
				else:
					self.value = float("%.*f" % (self.precision, float(value)))
					value = ("%.*f" % (self.precision, self.value)).split(".")

				# Check boundaries
				if self.min is not None and self.value < self.min:
					return self.setValue(self.min)
				elif self.max is not None and self.value > self.max:
					return self.setValue(self.max)

				if value[0].startswith("-"):
					value[0] = value[0][1:]
					neg = True
				else:
					neg = False

				ival = ""
				for i in range(0, len(value[0])):
					if ival and i % 3 == 0:
						ival = self.currencyThousandDelimiter + ival

					ival = value[0][-(i+1)] + ival

				self.widget.removeClass("is-invalid")
				return ("-" if neg else "") + ival + \
				       ((self.currencyDecimalDelimiter + value[1]) if len(value) > 1 else "") + \
				       " " + self.currency

			except Exception as e:
				logging.exception(e)

		self.widget.addClass("is-invalid")
		return value

	def onChange(self, event):
		self.widget["value"] = self.setValue(self.widget["value"])

	def unserialize(self, value=None):
		self.widget["value"] = self.setValue(value)

	def serialize(self):
		return self.value


class NumericViewWidget(NumericEditWidget):

	def __createWidget(self):
		return self

	def __configureWidget(self):
		pass

	def unserialize(self, value=None):
		self.value = value

		if value is None:
			value = conf["emptyValue"]
		else:
			value = self.setValue(value)

		self.appendChild(html5.TextNode(value), replace=True)


class NumericBone(BaseBone):
	editWidgetFactory = NumericEditWidget
	viewWidgetFactory = NumericViewWidget

	@staticmethod
	def checkFor(moduleName, boneName, skelStructure):
		return skelStructure[boneName]["type"] == "numeric" or skelStructure[boneName]["type"].startswith("numeric.")


boneSelector.insert(1, NumericBone.checkFor, NumericBone)

