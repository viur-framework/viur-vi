#-*- coding: utf-8 -*-
import html5
from priorityqueue import viewDelegateSelector
from config import conf

class InternalPreview( html5.Ul ):
	def __init__(self, modul, structure, item, *args, **kwargs):
		super( InternalPreview, self ).__init__( *args, **kwargs )

		self.addClass("sbw-internalpreview")

		tmpDict = {key: bone for key, bone in structure}

		for key, bone in structure:
			if "params" in bone.keys() and bone[ "params" ] \
					and "previewBone" in bone[ "params" ].keys() \
						and bone[ "params" ][ "previewBone" ] == False:
				continue

			self.ali= html5.Li()
			self.ali["class"]=[ modul,"type_"+bone["type"],"bone_"+key]
			self.adl= html5.Dl()

			self.adt=html5.Dt()
			self.adt.appendChild(html5.TextNode(key if conf["showBoneNames"] else bone.get("descr", key)))

			self.aadd=html5.Dd()
			delegateFactory = viewDelegateSelector.select( modul, key, tmpDict )( modul, key, tmpDict )
			self.aadd.appendChild(delegateFactory.render( item, key ))

			self.adl.appendChild(self.adt)
			self.adl.appendChild(self.aadd)
			self.ali.appendChild(self.adl)

			self.appendChild(self.ali)
