# -*- coding: utf-8 -*-
from vi import html5
from vi.priorityqueue import editBoneSelector, viewDelegateSelector
from vi.config import conf

class ColorViewBoneDelegate( object ):
	def __init__(self, moduleName, boneName, skelStructure, *args, **kwargs ):
		super( ColorViewBoneDelegate, self ).__init__()
		self.skelStructure = skelStructure
		self.boneName = boneName
		self.moduleName = moduleName

	def render( self, data, field ):
		if field in data.keys():
			color = html5.Div()
			color.addClass("vi-delegato-icon")
			color["style"]["background-Color"]=str( data[field])

			lbl = html5.Span(str( data[field]))
			lbl.addClass("vi-delegato-label")

			delegato = html5.Div()
			delegato.appendChild(color)
			delegato.appendChild(lbl)
		else:
			delegato = html5.Div(conf[ "emptyValue" ])

		delegato.addClass("vi-delegato", "vi-delegato--color")
		return delegato


class ColorEditBone( html5.Input ):

	def __init__(self, moduleName, boneName,readOnly, *args, **kwargs ):
		super( ColorEditBone,  self ).__init__( *args, **kwargs )
		self.boneName = boneName
		self.readOnly = readOnly
		self["type"]="color"
		if readOnly:
			self["disabled"]=True


	@staticmethod
	def fromSkelStructure(moduleName, boneName, skelStructure, *args, **kwargs):
		readOnly = "readonly" in skelStructure[ boneName ].keys() and skelStructure[ boneName ]["readonly"]
		return ColorEditBone(moduleName, boneName, readOnly)

	##read
	def unserialize(self, data, extendedErrorInformation=None):
		if self.boneName in data.keys():
			self._setValue(data[self.boneName])

	##save
	def serializeForPost(self):
		return { self.boneName: str(self._getValue())}

	##UNUSED
	def serializeForDocument(self):
		return self.serializeForPost()

def CheckForColorBone(moduleName, boneName, skelStucture, *args, **kwargs):
	return skelStucture[boneName]["type"] == "color"

#Register this Bone in the global queue
editBoneSelector.insert( 3, CheckForColorBone, ColorEditBone)
viewDelegateSelector.insert( 3, CheckForColorBone, ColorViewBoneDelegate)
