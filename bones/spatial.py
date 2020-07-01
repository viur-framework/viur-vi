# -*- coding: utf-8 -*-
from vi.priorityqueue import boneSelector
from vi.bones.base import BaseBone, BaseEditWidget, BaseViewWidget


class SpatialEditWidget(BaseEditWidget):

	def createWidget(self):
		return self.fromHTML(
			"""
			<ignite-input [name]="latitude" type="number" placeholder="latitude">
			<ignite-input [name]="longitude" type="number" placeholer="longitute">
			"""
		)

	def unserialize(self, value=None):
		self.latitude["value"], self.longitude["value"] = value or (0, 0)

	def serialize(self):
		return {
			"lat": self.latitude["value"],
			"lng": self.longitude["value"]
		}


class SpatialBone(BaseBone):
	editWidgetFactory = SpatialEditWidget

	@staticmethod
	def checkFor(moduleName, boneName, skelStructure):
		return skelStructure[boneName]["type"] == "spatial" or skelStructure[boneName]["type"].startswith("spatial.")


boneSelector.insert(1, SpatialBone.checkFor, SpatialBone)
