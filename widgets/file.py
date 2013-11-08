import html5
from widgets.tree import TreeWidget, LeafWidget
from priorityqueue import displayDelegateSelector

class LeafFileWidget( LeafWidget ):
	def __init__(self, modul, data, *args, **kwargs ):
		super( LeafFileWidget, self ).__init__( modul, data, *args, **kwargs )
		if "servingurl" in data.keys():
			self.appendChild( html5.Img( data["servingurl"]) )
		self["class"].append("file")

class FileWidget( TreeWidget ):
	leafWidget = LeafFileWidget

	@staticmethod
	def canHandle( modul, modulInfo ):
		print(modulInfo["handler"].startswith("tree.simple.file" ))
		return( modulInfo["handler"].startswith("tree.simple.file" ) )

displayDelegateSelector.insert( 3, FileWidget.canHandle, FileWidget )