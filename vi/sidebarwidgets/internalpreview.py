# -*- coding: utf-8 -*-
from flare import html5

from flare.viur import BoneSelector
from vi.config import conf
from flare.button import Button
from js import document

class InternalPreview( html5.Ul ):
	def __init__(self, module, structure, item, *args, **kwargs):
		super( InternalPreview, self ).__init__( *args, **kwargs )

		self.addClass("vi-sb-intprev box-body box--content")

		tmpDict = {key: bone for key, bone in structure.items()}

		for key, bone in structure.items():
			if "params" in bone.keys() and bone["params"] \
					and "previewBone" in bone["params"].keys() \
					and bone["params"]["previewBone"] == False:
				continue

			self.ipli = html5.Li()
			self.ipli["class"] = ["vi-sb-intprev-item", "vi-sb-intprev--" + module, "vi-sb-intprev--" + bone["type"],
								 "vi-sb-intprev--" + key]

			self.ipdl = html5.Dl()
			self.ipdl.addClass("vi-sb-intprev-content")


			self.ipdt = html5.Dt()
			self.ipdt.addClass("vi-sb-intprev-title")
			self.ipdt.appendChild(html5.TextNode(key if conf["showBoneNames"] else bone.get("descr", key)))

			self.ipdd = html5.Dd()
			self.ipdd.addClass("vi-sb-intprev-descr")
			boneFactory = BoneSelector.select(module, key, tmpDict)(module, key, tmpDict)

			if key == "key":
				keydiv = html5.Div()
				keydiv["style"]["display"] ="inline-block"
				copybtn = Button("Copy", self.onCopyKey)

				keyvaluediv = boneFactory.viewWidget(item[key])

				keyfield = html5.Input()
				keyfield["value"] = item[key]
				keyfield["style"]["opacity"] = 0
				keyfield["style"]["position"] = "absolute"
				keyfield["id"] = "keyfield"

				keydiv.appendChild(keyfield, keyvaluediv, copybtn)
				self.ipdd.appendChild(keydiv)
			else:
				self.ipdd.appendChild(boneFactory.viewWidget(item[key]))

			self.ipdl.appendChild(self.ipdt)
			self.ipdl.appendChild(self.ipdd)
			self.ipli.appendChild(self.ipdl)

			self.appendChild(self.ipli)

	def onCopyKey( self,btn ):
		akey = document.getElementById("keyfield")
		akey.select()
		akey.setSelectionRange(0, 99999)
		document.execCommand("copy")

