# -*- coding: utf-8 -*-
import html5, utils, re
from priorityqueue import editBoneSelector

class AmountBone(html5.Input):
	def __init__(self, moduleName, boneName, readOnly, currency=None, *args, **kwargs):
		super(AmountBone, self).__init__(*args, **kwargs)

		self.moduleName = moduleName
		self.boneName = boneName
		self.readOnly = readOnly
		self.currency = currency

		if self.readOnly:
			self.input["readonly"] = True

		self.value = None
		self.pat = re.compile("-?((\d{1,3}\.)*|\d*)[,]\d+|\d+")
		self.txt = re.compile(u"[A-Za-z_#?%äöüÄÖÜß]+")

		self.sinkEvent("onChange")

	def setValue(self, value):
		self.value = str(value).strip()

		if isinstance(value, float):
			self.value = self.value.replace(".", ",")

		if self.pat.match(self.value):
			try:
				val = re.sub("[^-0-9,]", "", self.value).replace(",", ".")
				self.value = float("%.2f" % float(val))

				val = str("%.2f" % self.value).split(".")
				if val[0].startswith("-"):
					val[0] = val[0][1:]
					neg = True
				else:
					neg = False

				ival = ""
				for i in range(0, len(val[0])):
					if ival and i % 3 == 0:
						ival = "." + ival

					ival = val[0][-(i + 1)] + ival

				self["value"] = ("-" if neg else "") + ival + "," + val[1] + self.currency
				return self["value"]

			except:
				pass

		return self.setValue("0")

	def onChange(self, e):
		self.setValue(self["value"])

	@staticmethod
	def fromSkelStructure(moduleName, boneName, skelStructure, *args, **kwargs):
		params = skelStructure[boneName].get("params")
		readOnly = skelStructure[boneName].get("readonly", False)

		currency = u"€"

		# View bone as readOnly even if it's not readOnly by system.
		if not readOnly and params:
			style = params.get("style", "").lower()
			for s in style.split(" "):
				if s == "readonly":
					readOnly = True

			currency = params.get("currency", "").lower()
			if currency:
				currency = {
					"euro": u"€",
					"dollar": u"$",
					"yen": u"¥",
					"pound": u"£",
					"baht": u"฿",
					"bitcoin": u"฿"
				}.get(currency, currency)

		return AmountBone(moduleName, boneName, readOnly, currency)

	def unserialize(self, data):
		self.setValue(data.get(self.boneName, "0"))

	def serializeForPost(self):
		return {
			self.boneName: str(self.value)
		}

	def serializeForDocument(self):
		return {
			self.boneName: self.value
		}

	def setExtendedErrorInformation(self, errorInfo):
		pass

	@staticmethod
	def checkFor(moduleName, boneName, skelStructure, *args, **kwargs):
		return (skelStructure[boneName]["type"] == "numeric.amount"
		        or skelStructure[boneName]["type"].startswith("numeric.amount."))

editBoneSelector.insert(5, AmountBone.checkFor, AmountBone)
