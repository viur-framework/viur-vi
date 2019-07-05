# -*- coding: utf-8 -*-
import html5
from priorityqueue import viewDelegateSelector
from config import conf

class InternalPreview( html5.Ul ):
	def __init__(self, module, structure, item, *args, **kwargs):
		super( InternalPreview, self ).__init__( *args, **kwargs )

		self.addClass("vi-sb-intprev box-body box--content")

		tmpDict = {key: bone for key, bone in structure}

		for key, bone in structure:
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
			delegateFactory = viewDelegateSelector.select(module, key, tmpDict)(module, key, tmpDict)
			self.ipdd.appendChild(delegateFactory.render(item, key))

			self.ipdl.appendChild(self.ipdt)
			self.ipdl.appendChild(self.ipdd)
			self.ipli.appendChild(self.ipdl)

			self.appendChild(self.ipli)
