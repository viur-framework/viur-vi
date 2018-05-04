#-*- coding: utf-8 -*-
from bones.base import BaseEditBone
from priorityqueue import editBoneSelector

class SerialEditBone(BaseEditBone):

	def __init__(self, moduleName, boneName, readonly = False, validChars=None, invalidChars=None,
	                    minLength = None, maxLength = None, fill = None, align = None, *args, **kwargs):

		super(SerialEditBone, self).__init__(moduleName, boneName, readOnly = readonly, *args, **kwargs)
		self.addClass("vi-serialbone", "vi-serialbone-%s" % boneName)

		self.validChars = validChars
		self.invalidChars = invalidChars
		self.minLength = minLength

		# Not supported HTML5 property for now
		#if self.minLength:
		#	self["minlength"] = self.minLength

		self.maxLength = maxLength

		if self.maxLength:
			self["maxlength"] = self.maxLength

		assert not fill or len(fill) == 1, "fill may only be one character long!"
		self.fill = fill

		if self.fill and align is None:
			align = "right"

		assert not align or align in ["left", "right"], "align must be 'left', 'right' or None."
		self.align = align

		self.sinkEvent("onChange")
		self.errorInfo = None

	def _setError(self):
		if self.errorInfo and self.parent() and len(self.errorInfo) == 1 and self.boneName in self.errorInfo:
			lbl = self.parent().children(0)
			if isinstance(lbl, html5.Label):
				lbl.addClass("is_invalid")
				lbl["title"] = self.errorInfo[self.boneName]

	def setExtendedErrorInformation(self, errorInfo):
		self.errorInfo = errorInfo
		self._setError()

	def onAttach(self):
		super(SerialEditBone, self).onAttach()
		self._setError()

	def format(self, value):
		if not self.align:
			return value

		if self.minLength:
			length = self.minLength
		elif self.maxLength:
			length = self.maxLength

			if self.fill and len(value) > length:
				if self.align == "right":
					while value.startswith(self.fill):
						value = value[1:]
				else:
					while value.endswith(self.fill):
						value = value[:1]
		else:
			return value

		fills = "".join([self.fill for _ in range(len(value), length)])
		return fills + value if self.align == "right" else value + fills

	def unserialize(self, data, **kwargs):
		if self.boneName in data.keys():
			self["value"] = self.format(str(data[self.boneName]) if data[self.boneName] else "")

	def onChange(self, event):
		self["value"] = self.format(self["value"])

		for c in ["value-too-short", "value-too-large", "has-invalid-chars"]:
			self.removeClass("vi-serialbone-%s" % c)

		css = []

		if self.minLength is not None and len(self["value"]) < self.minLength:
			css.append("value-too-short")
		elif self.maxLength is not None and len(self["value"]) > self.maxLength:
			css.append("value-too-large")

		if (self.validChars is not None and any([x not in self.validChars for x in self["value"]])
			or self.invalidChars is not None and any([x in self.invalidChars for x in self["value"]])):
			css.append("has-invalid-chars")

		for c in css:
			self.addClass("vi-serialbone-%s" % c)

	@classmethod
	def fromSkelStructure(cls, moduleName, boneName, skelStructure, *args, **kwargs):
		kwargs = {}

		for attName, defVal in {
			"readonly": False,
			"minLength": None,
			"maxLength": None,
			"validChars": None,
			"invalidChars": None,
			"fill": None,
			"align": None,
		}.items():
			kwargs[attName] = skelStructure[boneName].get(attName, defVal)

		return cls(moduleName, boneName, **kwargs)

	@staticmethod
	def checkFor(moduleName, boneName, skelStructure, *args, **kwargs):
		return (skelStructure[boneName]["type"] == "serial"
				or skelStructure[boneName]["type"].startswith("serial."))

editBoneSelector.insert(5, SerialEditBone.checkFor, SerialEditBone)
