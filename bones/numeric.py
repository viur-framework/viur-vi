# -*- coding: utf-8 -*-
import html5
from priorityqueue import editBoneSelector, viewDelegateSelector, extendedSearchWidgetSelector, extractorDelegateSelector
from event import EventDispatcher
from config import conf
from bones.base import BaseBoneExtractor

class NumericBoneExtractor(BaseBoneExtractor):

	def render(self, data, field):
		return str(self.raw(data, field)).replace(".", ",")

	def raw(self, data, field):
		if field in data.keys():
			value = data[field]

			if isinstance(value, int):
				return value

			elif isinstance(value, float):
				return round(value, self.skelStructure[field].get("precision", 2))

		return 0

class NumericViewBoneDelegate(object):
	def __init__(self, moduleName, boneName, skelStructure, *args, **kwargs):
		super(NumericViewBoneDelegate, self).__init__()

		self.skelStructure = skelStructure
		self.boneName = boneName
		self.moduleName = moduleName

	def render(self, data, field):
		value =  conf["empty_value"]
		if field in data.keys():
			try:
				prec = self.skelStructure[field].get("precision")

				if prec and data[field] is not None:
					value = ( "%." + str( prec ) + "f" ) % data[field]
				else:
					value = str(data[field])

			except:
				value = str(data[field])

		delegato = html5.Div(value)
		delegato.addClass("vi-delegato", "vi-delegato--numeric")
		return delegato

class NumericEditBone(html5.Div):
	def __init__(self, moduleName, boneName, readOnly, _min=False, _max=False, precision=False, currency=None,
	                *args, **kwargs ):
		super( NumericEditBone,  self ).__init__( *args, **kwargs )
		self.boneName = boneName
		self.readOnly = readOnly
		self.addClass("vi-bone-container")

		self.input = html5.ignite.Input()
		self.appendChild(self.input)

		if currency:
			self.appendChild(html5.Span(currency))

		self.input["type"] = "number"

		if _min:
			self.input["min"] = _min

		if _max:
			self.input["max"] = _max

		if precision:
			self.input["step"] = pow(10, -precision)
		else: #Precision is zero, treat as integer input
			self.input["step"] = 1

		if self.readOnly:
			self.input["readonly"] = True

	@staticmethod
	def fromSkelStructure(moduleName, boneName, skelStructure, *args, **kwargs):
		params = skelStructure[boneName].get("params")
		readOnly = skelStructure[boneName].get("readonly", False)

		currency = None

		# View bone as readOnly even if it's not readOnly by system.
		if not readOnly and params:
			style = params.get("style", "").lower()
			for s in style.split(" "):
				if s == "readonly":
					readOnly = True

				elif s.startswith("amount."):
					currency = s.split(".", 1)[1]
					currency = {
						"euro": u"€",
						"dollar": u"$",
						"yen": u"¥",
						"pound": u"£",
						"baht": u"฿",
						"bitcoin": u"฿"
					}.get(currency, currency)

		return NumericEditBone(moduleName, boneName, readOnly,
		                       skelStructure[boneName].get("min", False),
		                       skelStructure[boneName].get("max", False),
		                       skelStructure[boneName].get("precision", False),
		                       currency = currency)

	def unserialize(self, data):
		self.input["value"] = data.get(self.boneName, "")

	def serializeForPost(self):
		return {
			self.boneName: self.input["value"]
		}

	def serializeForDocument(self):
		return self.serializeForPost()

	def setExtendedErrorInformation(self, errorInfo ):
		pass

class ExtendedNumericSearch( html5.Div ):
	def __init__(self, extension, view, module, *args, **kwargs ):
		super( ExtendedNumericSearch, self ).__init__( *args, **kwargs )
		self.view = view
		self.extension = extension
		self.module = module
		self.opMode = extension["mode"]
		self.filterChangedEvent = EventDispatcher("filterChanged")
		assert self.opMode in ["equals","from", "to","range"]
		self.appendChild( html5.TextNode(extension["name"]))
		self.sinkEvent("onKeyDown")
		if self.opMode in ["equals","from", "to"]:
			self.input = html5.Input()
			self.input["type"] = "number"
			self.appendChild( self.input )
		elif self.opMode == "range":
			self.input1 = html5.Input()
			self.input1["type"] = "number"
			self.appendChild( self.input1 )
			self.appendChild( html5.TextNode("to") )
			self.input2 = html5.Input()
			self.input2["type"] = "number"
			self.appendChild( self.input2 )

	def onKeyDown(self, event):
		if html5.isReturn(event):
			self.filterChangedEvent.fire()

	def updateFilter(self, filter):
		if self.opMode=="equals":
			filter[ self.extension["target"] ] = self.input["value"]
		elif self.opMode=="from":
			filter[ self.extension["target"]+"$gt" ] = self.input["value"]
		elif self.opMode=="to":
			filter[ self.extension["target"]+"$lt" ] = self.input["value"]
		elif self.opMode=="prefix":
			filter[ self.extension["target"]+"$lk" ] = self.input["value"]
		elif self.opMode=="range":
			filter[ self.extension["target"]+"$gt" ] = self.input1["value"]
			filter[ self.extension["target"]+"$lt" ] = self.input2["value"]
		return( filter )

	@staticmethod
	def canHandleExtension(extension, view, module):
		return( isinstance( extension, dict) and "type" in extension.keys() and (extension["type"]=="numeric" or extension["type"].startswith("numeric.") ) )




def CheckForNumericBone(moduleName, boneName, skelStucture, *args, **kwargs):
	return skelStucture[boneName]["type"] == "numeric"

#Register this Bone in the global queue
editBoneSelector.insert( 3, CheckForNumericBone, NumericEditBone)
viewDelegateSelector.insert( 3, CheckForNumericBone, NumericViewBoneDelegate)
extendedSearchWidgetSelector.insert( 1, ExtendedNumericSearch.canHandleExtension, ExtendedNumericSearch )
extractorDelegateSelector.insert( 3, CheckForNumericBone, NumericBoneExtractor)
