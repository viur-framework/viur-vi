import html5
from priorityqueue import viewDelegateSelector

class InternalPreview( html5.Div ):
	def __init__(self, modul, structure, item, *args, **kwargs):
		super( InternalPreview, self ).__init__( *args, **kwargs )

		tmpDict = {}
		for key, bone in structure:
			tmpDict[ key ] = bone
		for key, bone in structure:
			self.ali= html5.Li()
			self.ali["class"]=[ modul,"type_"+bone["type"],"bone_"+key]
			self.adl= html5.Dl()

			self.adt=html5.Dt()
			self.adt.appendChild(html5.TextNode(bone["descr"]))

			self.aadd=html5.Dd()
			delegateFactory = viewDelegateSelector.select( modul, key, tmpDict )( modul, key, tmpDict )
			self.aadd.appendChild(delegateFactory.render( item, key ))

			self.adl.appendChild(self.adt)
			self.adl.appendChild(self.aadd)
			self.ali.appendChild(self.adl)

			self.appendChild(self.ali)