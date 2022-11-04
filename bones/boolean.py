# -*- coding: utf-8 -*-
from vi import html5
from vi.priorityqueue import editBoneSelector, viewDelegateSelector, extendedSearchWidgetSelector
from vi.config import conf
from vi.framework.event import EventDispatcher
from vi.i18n import translate


class BooleanViewBoneDelegate(object):
	def __init__(self, moduleName, boneName, skelStructure, *args, **kwargs):
		super(BooleanViewBoneDelegate, self).__init__()
		self.skelStructure = skelStructure
		self.boneName = boneName
		self.moduleName = moduleName

	def render(self, data, field):
		value = conf["emptyValue"]

		if field in data.keys():
			value = translate(str(data[field]))

		delegato = html5.Div(value)
		delegato.addClass("vi-delegato", "vi-delegato--bool")
		return delegato

class BooleanEditBone(html5.Div):

	def __init__(self, moduleName, boneName, readOnly, *args, **kwargs):
		super(BooleanEditBone, self).__init__(*args, **kwargs)
		self.boneName = boneName
		self.readOnly = readOnly
		self.addClass("vi-bone-container")

		switchWrap = html5.Div()
		switchWrap.addClass("switch ignt-switch")

		self.switch = html5.ignite.Switch()
		switchWrap.appendChild(self.switch)

		#switchLabel = html5.Label(forElem=self.switch)
		#switchLabel.addClass("switch-label")
		#switchWrap.appendChild(switchLabel)

		self.appendChild(switchWrap)

		if readOnly:
			self["disabled"] = True

	@staticmethod
	def fromSkelStructure(moduleName, boneName, skelStructure, *args, **kwargs):
		readOnly = "readonly" in skelStructure[boneName].keys() and skelStructure[boneName]["readonly"]
		return BooleanEditBone(moduleName, boneName, readOnly)

	def unserialize(self, data, extendedErrorInformation=None):
		if self.boneName in data.keys():
			self.switch._setChecked(data[self.boneName])

	def serializeForPost(self):
		return {self.boneName: str(self.switch._getChecked())}

	def serializeForDocument(self):
		return {self.boneName: self.switch._getChecked()}


class ExtendedBooleanSearch( html5.Div ):
	def __init__(self, extension, view, module, *args, **kwargs ):
		super( ExtendedBooleanSearch, self ).__init__( *args, **kwargs )
		self.view = view
		self.extension = extension
		self.module = module
		self.filterChangedEvent = EventDispatcher("filterChanged")
		self.appendChild(html5.TextNode(extension["name"]))
		self.selectionCb = html5.Select()
		self.appendChild(self.selectionCb)
		o = html5.Option()
		o["value"] = ""
		o.appendChild(html5.TextNode(translate("Ignore")))
		self.selectionCb.appendChild(o)
		o = html5.Option()
		o["value"] = "0"
		o.appendChild(html5.TextNode(translate("No")))
		self.selectionCb.appendChild(o)
		o = html5.Option()
		o["value"] = "1"
		o.appendChild(html5.TextNode(translate("Yes")))
		self.selectionCb.appendChild(o)
		self.sinkEvent("onChange")

	def onChange(self, event):
		event.stopPropagation()
		self.filterChangedEvent.fire()

	def updateFilter(self, filter):
		val = self.selectionCb["options"].item(self.selectionCb["selectedIndex"]).value
		if not val:
			if self.extension["target"] in filter.keys():
				del filter[self.extension["target"]]
		else:
			filter[self.extension["target"]] = val
		return (filter)

	@staticmethod
	def canHandleExtension( extension, view, module ):
		return( isinstance( extension, dict) and "type" in extension.keys() and (extension["type"]=="boolean" or extension["type"].startswith("boolean.") ) )


def CheckForBooleanBone(moduleName, boneName, skelStucture, *args, **kwargs):
	return skelStucture[boneName]["type"] == "bool"


# Register this Bone in the global queue
editBoneSelector.insert(3, CheckForBooleanBone, BooleanEditBone)
viewDelegateSelector.insert(3, CheckForBooleanBone, BooleanViewBoneDelegate)
extendedSearchWidgetSelector.insert(1, ExtendedBooleanSearch.canHandleExtension, ExtendedBooleanSearch)
